import aiohttp
import aiomysql
import aioredis
import motor.motor_asyncio

from celery import Celery

from config import config



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
    app['mongo_gridfs'] = motor.motor_asyncio.AsyncIOMotorGridFSBucket(client.util_aligner)


async def _create_sources_api_session(max_connections=None):
    limit = max_connections or config['SOURCES_API_LIMIT']

    return aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(),
            connector=aiohttp.TCPConnector(limit=limit))


async def create_sources_api_session(app):
    app['sources_api_session'] = await _create_sources_api_session()


async def dispose_sources_api_session(app):
    await app['sources_api_session'].close()
