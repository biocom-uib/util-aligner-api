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

# HTTP
# -----------------------------------------------------------------------------
CLIENT_MAX_SIZE = env('CLIENT_MAX_SIZE', 512 * 1024**2) # 512 MB

# CELERY
# -----------------------------------------------------------------------------
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='amqp://guest:guest@rabbitmq:5672//')
CELERY_TASK_DEFAULT_QUEUE = env('CELERY_TASK_DEFAULT_QUEUE', default='server_default')
ALIGNMENT_QUEUE = env('ALIGNMENT_QUEUE', default='server_aligner')
MULTIPLE_QUEUE = env('MULTIPLE_QUEUE', default='server_comparer')
CELERY_TASK_QUEUES = [
    Queue('server_default', routing_key='server_default',
          queue_arguments={'x-max-priority': 10})
    Queue(ALIGNMENT_QUEUE, routing_key=ALIGNMENT_QUEUE,
          queue_arguments={'x-max-priority': 10})
    Queue(MULTIPLE_QUEUE, routing_key=MULTIPLE_QUEUE,
          queue_arguments={'x-max-priority': 10})
]

SERVER_URL = env('SERVER_URL')
BASE_PATH = env('BASE_PATH')

EMAIL_FROM = env('EMAIL_FROM')
EMAIL_PASSWORD = env('EMAIL_PASSWORD')

# MONGO
MONGODB_URL = env('MONGODB_URL', default='mongodb://mongo/util_aligner')
