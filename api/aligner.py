from celery import Celery

from api.email import send_email

app_create = Celery('create', broker='amqp://localhost')
app_finished = Celery('finished', broker='amqp://localhost')


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


def server_create_job(data):
    if job_running(data):
        append_email(data)
        return
    cached, results = is_cached_job(data)
    if cached:
        return send_email(data, results, [data['email']])
    create_redis_job(data)
    start_job(data)


@app_create.task
def start_job(data):
    pass


@app_finished.task
def server_finished_job(db, data):
    emails = get_emails(data)
    results = get_results(db, data)
    return send_email(data, results, emails)
