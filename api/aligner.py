from api.email import send_email
from config import config


def job_running(data):
    return False


def append_email(data):
    pass


def create_redis_job(data):
    pass


def get_results(db, data):
    pass


def is_cached_job(data):
    return False, None


def get_emails(data):
    pass


def server_create_job(data, queue_connection):
    if job_running(data):
        append_email(data)
        return
    cached, results = is_cached_job(data)
    if cached:
        return send_email(data, results, [data['email']])
    create_redis_job(data)
    start_job(data, queue_connection)


def start_job(data, queue_connection):
    queue_connection.send_task('process_alignment', (data,),
                               queue=config['ALIGNMENT_QUEUE'],
                               queue_arguments={'x-max-priority': 10})


def server_finished_job(db, data):
    emails = get_emails(data)
    results = get_results(db, data)
    return send_email(data, results, emails)
