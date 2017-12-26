from celery import Celery

from settings_celery import settings


app = Celery('util-aligner')
app.config_from_object(settings, namespace='CELERY')