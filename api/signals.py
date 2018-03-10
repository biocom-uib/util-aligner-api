import aiomysql
import redis

from settings import settings


async def _create_db_pool(max_connections=None, master=True):
    db_conf = settings['database_async'] if master else settings['database_ro']
    max_connections = max_connections or db_conf['pool']
    return await aiomysql.create_pool(
        host=db_conf['host'], port=db_conf['port'], user=db_conf['user'],
        password=db_conf['pwd'], db=db_conf['db'], charset='utf8', minsize=1,
        maxsize=max_connections)


async def create_db_pool(app):
    app['master_pool'] = await _create_db_pool()
    app['slave_pool'] = await _create_db_pool(master=False)


async def dispose_db_pool(app):
    app['slave_pool'].close()
    app['master_pool'].close()
    await app['slave_pool'].wait_closed()
    await app['master_pool'].wait_closed()


def create_sentry(app):
    import os
    from raven import Client, fetch_git_sha
    from raven_aiohttp import AioHttpTransport

    base_dir = os.path.dirname(os.path.dirname(__file__))

    app['sentry'] = Client(
        settings['sentry_dsn'],
        transport=AioHttpTransport,
        environment=settings['env'],
        release=fetch_git_sha(base_dir))


async def dispose_sentry(app):
    app['sentry'].remote.get_transport().close()


def _create_cache_pool():
    return redis.ConnectionPool(
        **dict(zip(('host', 'port', 'db'), settings["redis"].split())),
        max_connections=1000)


def create_cache_pool(app):
    app['redis_pool'] = _create_cache_pool()
