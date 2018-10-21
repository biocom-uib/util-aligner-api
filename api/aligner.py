from asyncio import get_event_loop
from bson.objectid import ObjectId
import hashlib
import json

from api.email import send_email_suspended, send_email_comparison_suspended
from config import config
from uuid import uuid4
from constants import MULTIPLE_ALIGNMENT_FINSIHED, PROCESS_TASK, MULTIPLE_ALIGNER_TASK, QUEUE_DISPATCHER

async def append_email(cache_connection, job_id, mail):
    email_key = create_email_key(job_id)
    previous_emails = await cache_connection.get(email_key)
    new_emails = f"{previous_emails.decode('utf-8')},{mail}"
    await cache_connection.set(email_key, new_emails)


def create_email_key(job_id):
    return f"{job_id}_mail"


def create_data_key(data):
    mail = data.pop('mail')
    job_id = None
    if 'job_id' in data:
        job_id = data.pop('job_id')
    data_dump = json.dumps(data, sort_keys=True)
    sha1 = hashlib.sha1(data_dump.encode('utf-8'))
    data['mail'] = mail
    if job_id:
        data['job_id'] = job_id
    return sha1.hexdigest()


async def create_redis_job(cache_connection, data):
    job_id = uuid4()
    data['job_id'] = job_id
    email_key = create_email_key(job_id)
    await cache_connection.set(email_key, data['mail'])
    data_key = create_data_key(data)
    await cache_connection.set(data_key, str(job_id))
    await cache_connection.set(str(job_id), data_key)
    return str(job_id)


async def get_results(mongo_db, mongo_gridfs, result_id):
    return await mongo_db.results.find_one({'_id': ObjectId(result_id)})

async def get_cached_job(db, cache_connection, mongo_db, mongo_gridfs, data):
    job_id = await cache_connection.get(create_data_key(data))
    if job_id:
        job_id = job_id.decode('utf-8')
        if job_id.startswith("FINISHED_"):
            result_id = job_id[len("FINISHED_"):]
            return None, await get_results(mongo_db, mongo_gridfs, result_id)
        return job_id, None
    return None, None


async def get_emails_from_job_id(cache_connection, job_id, result_id):
    data_key = await cache_connection.get(job_id)
    emails = await cache_connection.get(create_email_key(job_id))

    await cache_connection.set(data_key, f"FINISHED_{result_id}")

    return emails.decode('utf-8').split(',')


async def server_create_job_one_aligner(db, cache_connection, queue_connection, mongo_db,
                            mongo_gridfs, data):
    job_id, results = await get_cached_job(db, cache_connection, mongo_db,
                                           mongo_gridfs, data)
    if results:
        print('alignment already computed, sending email')
        get_event_loop().create_task(send_email_suspended(results, [data['mail']], mongo_gridfs))

    elif job_id:
        await append_email(cache_connection, job_id, data['mail'])
        print('alignment already queued, added email address to mailing')

    else:
        job_id = await create_redis_job(cache_connection, data)
        start_job(data, queue_connection)
        print('submited new job:', data)

    return job_id


async def server_create_job_one_aligner(db, cache_connection, queue_connection, mongo_db,
                            mongo_gridfs, data):
    aligners = []
    jobs_ids = []
    for aligner in data['aligners']:
        data['aligner'] = aligner
        job_id = server_create_job_one_aligner(db, cache_connection, queue_connection, mongo_db,
                                               mongo_gridfs, data)
        jobs_ids.append(job_id)
        aligners.append(aligner)
    if len(aligners) > 1:
        await create_redis_multiple_alignment(cache_connection, job_ids)
    return jobs_id


def start_job(data, queue_connection, task=PROCESS_TASK):
    queue_connection.send_task(task, (data,),
                               queue=QUEUE_DISPATCHER[task],
                               queue_arguments={'x-max-priority': 10})


async def server_finished_job(mongo_db, mongo_gridfs, cache_connection, job_id, result_id):
    emails = await get_emails_from_job_id(cache_connection, job_id, result_id)
    results = await get_results(mongo_db, mongo_gridfs, result_id)
    pending, jobs_id = await check_pending_alignments(cache_connection, job_id)
    if pending == MULTIPLE_ALIGNMENT_FINSIHED:
        start_job(jobs_id, queue_connection, task=MULTIPLE_ALIGNER_TASK)
    get_event_loop().create_task(send_email_suspended(results, emails, mongo_gridfs))


async def create_redis_multiple_alignment(cache_connection, jobs_ids):
    job_id = uuid4()
    for simple_job_id in jobs_ids:
        await cache_connection.set(f'MULTIPLE_{simple_job_id}', job_id)
    await cache_connection.set(f'PENDING_{job_id}', json.dumps(job_ids))
    await cache_connection.set(f'ALL_{job_id}', json.dumps(job_ids))


async def check_pending_alignments(cache_connection, job_id):
    multiple_job_id = await cache_connection.get(f'MULTIPLE_{job_id}')
    pending = None
    if multiple_job_id:
        pass
    return pending, {'results_object_ids': [], 'job_id': multiple_job_id}
    

async def server_finished_aligner(mongo_db, mongo_gridfs, cache_connection, job_id, result_id):
    emails = await get_emails_from_job_id(cache_connection, job_id, result_id)
    results = await get_results(mongo_db, mongo_gridfs, result_id)
    get_event_loop().create_task(send_email_suspended_comparison(results, emails, mongo_gridfs))


async def server_finished_multiple_job(mongo_db, mongo_gridfs, cache_connection, job_id, result_id):
    await server_finished_job(mongo_db, mongo_gridfs, cache_connection, job_id, result_id):
