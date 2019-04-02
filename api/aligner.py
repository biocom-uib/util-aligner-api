from asyncio import get_event_loop
from aioredlock import Aioredlock, LockError
from bson.objectid import ObjectId
from contextlib import asynccontextmanager
from copy import deepcopy
import hashlib
import json

from api.email import send_email_alignment, send_email_comparison
from config import config
from uuid import uuid4
from api.v2.constants import PROCESS_TASK, COMPARE_TASK, QUEUE_DISPATCHER

LOCK_MANAGER = None
DATA_CACHE_LOCK = "DATA_CACHE_LOCK"
JOB_GROUPS_LOCK = "JOB_GROUPS_LOCK"


@asynccontextmanager
async def locked(cache_connection, lock_key):
    global LOCK_MANAGER

    if LOCK_MANAGER is None:
        LOCK_MANAGER = Aioredlock(redis_connections=[cache_connection], lock_timeout=3600, retry_count=300)

    async with await LOCK_MANAGER.lock(lock_key) as lock:
        assert lock.valid
        yield


def create_job_id():
    return str(uuid4())

def create_data_key(data):
    data_dump = json.dumps(data, sort_keys=True)
    sha1 = hashlib.sha1(data_dump.encode('utf-8')).hexdigest()

    return f'JOB_{sha1}'

def create_result_key(job_id):
    return f'RESULT_{job_id}'

def create_email_key(job_id):
    return f'EMAILS_{job_id}'


async def get_alignment(mongo_db, mongo_gridfs, result_id):
    return await mongo_db.alignments.find_one({'_id': ObjectId(result_id)})

async def get_comparison(mongo_db, mongo_gridfs, result_id):
    return await mongo_db.comparisons.find_one({'_id': ObjectId(result_id)})

async def get_job_result_id(cache_connection, job_id):
    result_id = await cache_connection.get(create_result_key(job_id))

    if result_id is not None:
        result_id = result_id.decode('utf-8')

    return result_id


async def get_email_list(cache_connection, job_id):
    return [email.decode('utf-8') for email in await cache_connection.smembers(create_email_key(job_id))]

async def append_email(cache_connection, job_id, email):
    email_key = create_email_key(job_id)
    await cache_connection.sadd(email_key, email)

async def delete_email_list(cache_connection, job_id):
    email_key = create_email_key(job_id)
    await cache_connection.delete(email_key)

async def get_and_delete_email_list(cache_connection, job_id):
    emails = await get_email_list(cache_connection, job_id)
    await delete_email_list(cache_connection, job_id)
    return emails


async def create_redis_job_if_needed(cache_connection, data, emails=[]):
    data_key = create_data_key(data)
    new_job_id = create_job_id()

    # reserve cache_key for job_id if not already present
    async with locked(cache_connection, DATA_CACHE_LOCK):
        await cache_connection.set(data_key, new_job_id, exist=cache_connection.SET_IF_NOT_EXIST)
        job_id = await cache_connection.get(data_key)
        job_id = job_id.decode('utf-8')

        is_new = job_id == new_job_id

        # inside lock or the job could finish while we are appending the email
        for email in emails:
            await append_email(cache_connection, job_id, email)

        if is_new:
            print(f'initializing new job {job_id} for data_key {data_key}')

            result_key = create_result_key(job_id)
            await cache_connection.set(result_key, '')

            result_id = None

        else:
            result_id = await get_job_result_id(cache_connection, job_id)

            if result_id:
                print(f'found finished job {job_id} for data_key {data_key} with result {result_id}')
            else:
                print(f'found pending job {job_id} for data_key {data_key}')

    return job_id, is_new, result_id


async def cache_job_result(cache_connection, job_id, result_id):
    result_key = create_result_key(job_id)
    await cache_connection.set(result_key, result_id)


def submit_task(data, queue_connection, task=PROCESS_TASK):
    print('queued new task:', data)

    queue_connection.send_task(task, (data,),
                               queue=QUEUE_DISPATCHER[task],
                               queue_arguments={'x-max-priority': 10})



async def create_redis_job_group(cache_connection, group_id, job_ids, email):
    async with locked(cache_connection, JOB_GROUPS_LOCK):
        print(f"initializing job group {group_id} with jobs {job_ids}")

        for job_id in job_ids:
            await cache_connection.sadd(f'GROUPS_{job_id}', group_id)

        await cache_connection.set(f'NJOBS_{group_id}', len(job_ids))
        await append_email(cache_connection, group_id, email)


async def get_job_group_status(cache_connection, group_id):
    async with locked(cache_connection, JOB_GROUPS_LOCK):
        return await _get_job_group_status(cache_connection, group_id)


# JOB_GROUPS_LOCK locked
async def _get_job_group_status(cache_connection, group_id):
    njobs_exists = await cache_connection.exists(f'NJOBS_{group_id}')
    done_exists = await cache_connection.exists(f'DONE_{group_id}')

    if done_exists:
        # all completed
        done = await cache_connection.lrange(f'DONE_{group_id}', 0, -1)
        done = [done_job.decode('utf-8') for done_job in done]
    else:
        done = []

    if njobs_exists:
        njobs = int(await cache_connection.get(f'NJOBS_{group_id}'))
    elif done_exists:
        njobs = len(done)
    else:
        njobs = 0

    if done and len(done) == njobs:
        results = {job_id: await get_job_result_id(cache_connection, job_id) for job_id in done}
    else:
        results = {}

    return {'njobs': njobs, 'done': done, 'results': results}


# JOB_GROUPS_LOCK locked
async def _delete_redis_job_group(cache_connection, group_id):
    print(f"deleting job group {group_id}")

    await cache_connection.delete(f'NJOBS_{group_id}')

    # allow programmatic access (caching)
    # await cache_connection.delete(f'DONE_{group_id}')


# JOB_GROUPS_LOCK locked
async def _update_redis_job_group(cache_connection, group_id, job_id):
    print(f"job {job_id} of group {group_id} finished")

    group_njobs = await cache_connection.get(f'NJOBS_{group_id}')
    group_njobs = group_njobs.decode('utf-8')

    await cache_connection.lpush(f'DONE_{group_id}', job_id)
    num_done = await cache_connection.llen(f'DONE_{group_id}')

    emails = await get_email_list(cache_connection, group_id)

    if group_njobs == str(num_done):
        jobs = await cache_connection.lrange(f'DONE_{group_id}', 0, -1)
        jobs = [job_id.decode('utf-8') for job_id in jobs]

        group_results = [await get_job_result_id(cache_connection, job_id) for job_id in jobs]

        print(f"all jobs of group {group_id} finished with results {group_results}")

        await _delete_redis_job_group(cache_connection, group_id)
        await delete_email_list(cache_connection, group_id)

        return group_results, emails

    else:
        return None, emails


async def update_redis_job_groups(cache_connection, job_id):
    completed_groups = {}
    emails = set()

    async with locked(cache_connection, JOB_GROUPS_LOCK):
        for group_id in await cache_connection.smembers(f'GROUPS_{job_id}'):
            group_id = group_id.decode('utf-8')

            group_results, group_emails = await _update_redis_job_group(cache_connection, group_id, job_id)
            emails.update(group_emails)

            if group_results is not None:
                completed_groups[group_id] = {'emails': group_emails, 'results_object_ids': sorted(group_results)}

        await cache_connection.delete(f'GROUPS_{job_id}')

    return completed_groups, emails


async def server_create_alignment_job_group(cache_connection, queue_connection, mongo_db, mongo_gridfs, data):
    aligners = data.pop('aligners')
    email = data.pop('mail')
    jobs = []

    for aligner in aligners:
        data['aligner'] = aligner
        job_id, is_new, result_id = await create_redis_job_if_needed(cache_connection, data, emails=[] if len(aligners) > 1 else [email])
        del data['aligner']
        jobs.append((aligner, job_id, is_new, result_id))

    if len(aligners) > 1:
        group_id = create_job_id()
        job_ids = [job_id for aligner, job_id, is_new, result_id in jobs]

        await create_redis_job_group(cache_connection, group_id, job_ids, email)

    for aligner, job_id, is_new, result_id in jobs:
        if is_new:
            data_copy = deepcopy(data)
            data_copy['job_id'] = job_id
            data_copy['aligner'] = aligner

            submit_task(data_copy, queue_connection)

        elif result_id:
            await server_finished_alignment(mongo_db, mongo_gridfs, cache_connection, queue_connection, job_id, result_id)

    return group_id if len(aligners) > 1 else job_id


async def server_create_comparison_job(mongo_db, mongo_gridfs, cache_connection, queue_connection, group_id, comparison_data):
    print(f"setting up comparison job for job group {group_id}")

    comparison_emails = comparison_data.pop('emails')

    comparison_job_id, comparison_is_new, comparison_result_id = \
        await create_redis_job_if_needed(cache_connection, comparison_data, emails=comparison_emails)

    if comparison_is_new:
        comparison_data['job_id'] = comparison_job_id
        submit_task(comparison_data, queue_connection, task=COMPARE_TASK)

    elif comparison_result_id:
        await server_finished_comparison(mongo_db, mongo_gridfs, cache_connection, comparison_job_id, comparison_result_id)


async def server_finished_alignment(mongo_db, mongo_gridfs, cache_connection, queue_connection, job_id, result_id):
    print(f"alignment finished: job_id={job_id} result_id={result_id}")

    emails = set()

    async with locked(cache_connection, DATA_CACHE_LOCK):
        await cache_job_result(cache_connection, job_id, result_id)
        emails.update(await get_and_delete_email_list(cache_connection, job_id))

    completed_groups, group_emails = await update_redis_job_groups(cache_connection, job_id)
    emails.update(group_emails)
    emails -= {''}

    async def get_results_and_send_email():
        results = await get_alignment(mongo_db, mongo_gridfs, result_id)
        await send_email_alignment(results, emails, mongo_gridfs)

    if emails:
        get_event_loop().create_task(get_results_and_send_email())

    for group_id, group_data in completed_groups.items():
        ids = group_data.get('results_object_ids', [])
        if len(ids) > 1:
            await server_create_comparison_job(mongo_db, mongo_gridfs, cache_connection, queue_connection, group_id, group_data)


async def server_finished_comparison(mongo_db, mongo_gridfs, cache_connection, job_id, result_id):
    print(f"comparison job finished: job_id={job_id} result_id={result_id}")

    emails = set()

    async with locked(cache_connection, DATA_CACHE_LOCK):
        await cache_job_result(cache_connection, job_id, result_id)
        emails.update(await get_and_delete_email_list(cache_connection, job_id))

    emails -= {''}

    async def get_results_and_send_emails():
        comparison_results = await get_comparison(mongo_db, mongo_gridfs, result_id)
        await send_email_comparison(comparison_results, emails, mongo_gridfs)

    if emails:
        get_event_loop().create_task(get_results_and_send_emails())
