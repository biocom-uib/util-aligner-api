"""
Base settings for Util Aligner API.
"""
import environs
from kombu import Queue
from pathlib import Path


# (util-aligner-api/config/base.py - 2 = util-aligner-api/)
ROOT_DIR = Path(__file__).parent.parent

# Load operating system environment variables and then prepare to use them
env = environs.Env()

# Operating System Environment variables have precedence over variables
# defined in the .env file, that is to say variables from the .env files
# will only be used if not defined as environment variables.
env_file = str(ROOT_DIR/'.env')
print('Loading : {}'.format(env_file))
env.read_env(env_file, False)
print('The .env file has been loaded. See base.py for more information')


# DEBUG
# -----------------------------------------------------------------------------
DEBUG = env.bool('DEBUG', default=False)

# APPLICATION-SPECIFIC
SERVER_URL = env('SERVER_URL')
BASE_PATH = env('BASE_PATH')

EMAIL_FROM = env('EMAIL_FROM')
EMAIL_PASSWORD = env('EMAIL_PASSWORD')

# HTTP
# -----------------------------------------------------------------------------
SOURCES_API_HOST = env('SOURCES_API_HOST', 'http://sources-api')
SOURCES_API_LIMIT = env.int('SOURCES_API_LIMIT', 100)

CLIENT_MAX_SIZE = env.int('CLIENT_MAX_SIZE', 512 * 1024**2) # 512 MB

# CELERY
# -----------------------------------------------------------------------------
class CelerySettings(object): pass

CELERY = CelerySettings()

CELERY.broker_url = env('CELERY_BROKER_URL', default='amqp://guest:guest@rabbitmq:5672//')
CELERY.task_default_queue = env('CELERY_TASK_DEFAULT_QUEUE', default='server_default')
alignment_queue = env('ALIGNMENT_QUEUE', default='server_aligner')
multiple_queue = env('MULTIPLE_QUEUE', default='server_comparer')
CELERY.task_queues = [
    Queue('server_default', routing_key='server_default',
          queue_arguments={'x-max-priority': 10}),
    Queue(alignment_queue, routing_key=alignment_queue,
          queue_arguments={'x-max-priority': 10}),
    Queue(multiple_queue, routing_key=multiple_queue,
          queue_arguments={'x-max-priority': 10})
]

# CACHING
# -----------------------------------------------------------------------------
REDIS_DSN = env('REDIS_DSN', default='redis 6379 0')
REDIS_URL = env('REDIS_URL', default='redis://redis')
MAX_SIZE_REDIS = env('MAX_SIZE_REDIS', default=10)

# MONGO
MONGODB_URL = env('MONGODB_URL', default='mongodb://mongo/util_aligner')
