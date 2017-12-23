import os

accesslog = '-'
access_log_format = '%a %l %u %t "%r" %s %b "%{Referrer}i" "%{User-Agent}i" %Tf'    # noqa

api_log = '-'
api_log_format = '%a %l %u %t "%r" %s %b "%{Referrer}i" "%{User-Agent}i" %Tf'    # noqa

bind = ['0.0.0.0:8080']
workers = 4
worker_class = 'aiohttp.worker.GunicornWebWorker'
reload = True
