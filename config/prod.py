"""
Production settings for Util Aligner API.
"""
import environs


# Load operating system environment variables and then prepare to use them
env = environs.Env()

HEADERS = {'Access-Control-Allow-Origin': 'biocom.uib.es/~adria/'}


# SENTRY CONFIGURATION
# -----------------------------------------------------------------------------
SENTRY_DSN = env('SENTRY_DSN')
SENTRY_ENVIRON = env('SENTRY_ENVIRON', default='production')
