import hashlib
import json
from bson.objectid import ObjectId

from api.email import send_email
from config import config
from uuid import uuid4


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
    data['job_id'] = uuid4()
    email_key = create_email_key(data['job_id'])
    await cache_connection.set(email_key, data['mail'])
    data_key = create_data_key(data)
    await cache_connection.set(data_key, str(data['job_id']))
    await cache_connection.set(str(data['job_id']), data_key)


async def get_results(db, result_id):
    return await db.results.find_one({'_id': ObjectId(result_id)})


async def get_cached_job(db, cache_connection, mongo_db, data):
    job_id = await cache_connection.get(create_data_key(data))
    if job_id:
        job_id = job_id.decode('utf-8')
        if job_id.startswith("FINISHED_"):
            result_id = job_id[len("FINISHED_"):]
            return None, await get_results(mongo_db, result_id)
        return job_id, None
    return False, None


def get_emails(data):
    return ['adria.alcala@gmail.com']


async def get_data_from_job_id(cache_connection, job_id, result_id):
    data_key = await cache_connection.get(job_id)
    emails = await cache_connection.get(create_email_key(job_id))

    await cache_connection.set(data_key, f"FINISHED_{result_id}")

    db, net1, net2, aligner = data_key.decode('utf-8').split('_')
    data = {
        'db': db,
        'net1': net1,
        'net2': net2,
        'aligner': aligner
    }
    emails = emails.decode('utf-8').split(',')
    return data, emails


async def server_create_job(db, cache_connection, queue_connection, mongo_db,
                            data):
    job_id, results = await get_cached_job(db, cache_connection, mongo_db,
                                           data)
    if results:
        return send_email(data, results, [data['mail']])
    if job_id:
        await append_email(cache_connection, job_id, data['mail'])
        return

    await create_redis_job(cache_connection, data)
    start_job(data, queue_connection)


def start_job(data, queue_connection):
    queue_connection.send_task('process_alignment', (data,),
                               queue=config['ALIGNMENT_QUEUE'],
                               queue_arguments={'x-max-priority': 10})


async def server_finished_job(db, cache_connection, job_id, result_id):
    data, emails = await get_data_from_job_id(cache_connection, job_id, result_id)
    results = await get_results(db, result_id)
    return send_email(data, results, emails)
