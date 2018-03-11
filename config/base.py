"""
Base settings for Util Aligner API.
"""
import environs
from pathlib import Path


# (util-aligner-api/config/base.py - 2 = util-aligner-api/)
ROOT_DIR = Path(__file__).parent.parent

# Load operating system environment variables and then prepare to use them
env = environs.Env()

READ_DOT_ENV_FILE = env.bool('READ_DOT_ENV_FILE', default=False)

if READ_DOT_ENV_FILE:
    # Operating System Environment variables have precedence over variables
    # defined in the .env file, that is to say variables from the .env files
    # will only be used if not defined as environment variables.
    env_file = str(ROOT_DIR/'.env')
    print('Loading : {}'.format(env_file))
    env.read_env(env_file, False)
    print('The .env file has been loaded. See base.py for more information')

# CACHING
# -----------------------------------------------------------------------------
REDIS_DSN = env('REDIS_DSN', default='redis 6379 0')
REDIS_URL = env('REDIS_URL', default='redis://redis')
MAX_SIZE_REDIS = env('MAX_SIZE_REDIS', default=10)


# DATABASE
# -----------------------------------------------------------------------------
DATABASE_DSN = env('DB_DSN', 'mysql+pymysql://puser:puser@mysql/protein_db')
DATABASE_HOST = env('DB_HOST', 'mysql')
DATABASE_PORT = int(env('DB_PORT', 3306))
DATABASE_USER = env('DB_USER', 'puser')
DATABASE_PASSWORD = env('DB_PASS', 'puser')
DATABASE_DB = env('DB_NAME', 'protein_db')
DATABASE_MAXSIZE = env('DB_MAX_POOL', 50)


# DEBUG
# -----------------------------------------------------------------------------
DEBUG = env.bool('DEBUG', default=False)

# CELERY
# -----------------------------------------------------------------------------
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='amqp://guest:guest@aligner.rabbitmq:5672//')
CELERY_TASK_DEFAULT_QUEUE = env('CELERY_TASK_DEFAULT_QUEUE', default='util_aligner')
