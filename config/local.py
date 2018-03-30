"""
Local settings for Util Aligner API.
"""
import environs

from config.base import *  # noqa


# Load operating system environment variables and then prepare to use them
env = environs.Env()

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