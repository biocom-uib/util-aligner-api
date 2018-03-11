"""
Production settings for Util Aligner API.
"""
import environs

from config.base import *  # noqa


# Load operating system environment variables and then prepare to use them
env = environs.Env()

HEADERS = {'Access-Control-Allow-Origin': 'biocom.uib.es/~adria/'}


# SENTRY CONFIGURATION
# -----------------------------------------------------------------------------
SENTRY_DSN = env('SENTRY_DSN', default='')
SENTRY_ENVIRON = env('SENTRY_ENVIRON', default='production')
