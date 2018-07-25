import aiomysql
import aioredis
import motor.motor_asyncio

from celery import Celery

from config import config


async def _create_db_pool(max_connections=None):
    max_connections = max_connections or config['DATABASE_MAXSIZE']
    return await aiomysql.create_pool(
        host=config['DATABASE_HOST'], port=config['DATABASE_PORT'], user=config['DATABASE_USER'],
        password=config['DATABASE_PASSWORD'], db=config['DATABASE_DB'], charset='utf8', minsize=1,
        maxsize=max_connections)


async def create_db_pool(app):
    app['master_pool'] = await _create_db_pool()


async def dispose_db_pool(app):
    app['master_pool'].close()
    await app['master_pool'].wait_closed()


def create_sentry(app):
    import os
    from raven import Client, fetch_git_sha
    from raven_aiohttp import AioHttpTransport

    base_dir = os.path.dirname(os.path.dirname(__file__))

    app['sentry'] = Client(
        config['SENTRY_DSN'],
        transport=AioHttpTransport,
        environment=config['env'],
        release=fetch_git_sha(base_dir))


async def dispose_sentry(app):
    app['sentry'].remote.get_transport().close()


async def _create_cache_pool():
    return await aioredis.create_redis_pool(
        config['REDIS_URL'],
        maxsize=config['MAX_SIZE_REDIS'])


async def create_cache_pool(app):
    app['redis_pool'] = await _create_cache_pool()


async def create_celery_app(app):
    celery_app = Celery()
    celery_app.config_from_object(config, namespace='CELERY')
    app['celery'] = celery_app


async def create_mongo(app):
    client = motor.motor_asyncio.AsyncIOMotorClient(config['MONGODB_URL'])
    app['mongo_db'] = client.util_aligner
