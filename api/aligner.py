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
    return f"{data['db']}_{data['net1']}_{data['net2']}_{data['aligner']}"


async def create_redis_job(cache_connection, data):
    data['job_id'] = uuid4()
    email_key = create_email_key(data['job_id'])
    await cache_connection.set(email_key, data['mail'])
    data_key = create_data_key(data)
    await cache_connection.set(data_key, str(data['job_id']))
    await cache_connection.set(str(data['job_id']), data_key)


async def get_results(db, data):
    return [{data['net1']: f'node_{i}', data['net2']: f'node_{i}'}
            for i in range(100)]


async def get_cached_job(db, cache_connection, data):
    job_id = await cache_connection.get(create_data_key(data))
    if job_id:
        if job_id == b'FINISHED':
            return None, await get_results(db, data)
        return job_id.decode('utf-8'), None
    return False, None


def get_emails(data):
    return ['adria.alcala@gmail.com']


async def get_data_from_job_id(cache_connection, job_id):
    data_key = await cache_connection.get(job_id)
    emails = await cache_connection.get(create_email_key(job_id))
    await cache_connection.set(data_key, 'FINISHED')
    db, net1, net2, aligner = data_key.decode('utf-8').split('_')
    data = {
        'db': db,
        'net1': net1,
        'net2': net2,
        'aligner': aligner
    }
    emails = emails.decode('utf-8').split(',')
    return data, emails


async def server_create_job(db, cache_connection, queue_connection, data):
    job_id, results = await get_cached_job(db, cache_connection, data)
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


async def server_finished_job(db, cache_connection, job_id):
    data, emails = await get_data_from_job_id(cache_connection, job_id)
    results = await get_results(db, data)
    return send_email(data, results, emails)
