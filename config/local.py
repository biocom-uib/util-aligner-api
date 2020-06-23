"""
Local settings for Util Aligner API.
"""
import environs

from config.base import *  # noqa


# Load operating system environment variables and then prepare to use them
env = environs.Env()


# DATABASE
# -----------------------------------------------------------------------------
# DATABASE_DSN = env('DATABASE_DSN', 'mysql+pymysql://puser:puser@mysql/protein_db')
# DATABASE_HOST = env('DATABASE_HOST', 'mysql')
# DATABASE_PORT = int(env('DATABASE_PORT', 3306))
# DATABASE_USER = env('DATABASE_USER', 'puser')
# DATABASE_PASSWORD = env('DATABASE_PASSWORD', 'puser')
# DATABASE_DB = env('DATABASE_NAME', 'protein_db')
# DATABASE_MAXSIZE = env('DATABASE_MAX_POOL', 50)
