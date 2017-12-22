import asyncio
from concurrent.futures._base import CancelledError

from aiohttp.web import HTTPException
from aiomysql import create_pool as mysql_aiopool
import redis

from settings import settings


loop = asyncio.get_event_loop()

"""
Redis connection acquisition and release is automatically
managed by StrictRedis:

    - When a redis command is invoked using StrictRedis
      a new connection is acquired from the pool, so the
      connection is unique to each command execution
      (set, get, incr...)

    - The command is executed inside a try, except, finally block

    - No matter what happens with the command execution
      in the finally block there is a pool.release(connection),
      so the connection is always released to the pool.

    - Redis Connection pool is threadsafe
"""
REDIS_POOL_SIZE = 1000
redis_conn_pool = redis.ConnectionPool(
    **dict(zip(('host', 'port', 'db'), settings["redis"].split())),
    max_connections=REDIS_POOL_SIZE)


db_pool = None
slave_db_pool = None


async def create_db_pool(max_connections=None, db_conf=None, pool_loop=None):
    db_conf = db_conf or settings['database_async']
    max_connections = max_connections or db_conf['pool']
    pool_loop = pool_loop or loop
    return await mysql_aiopool(host=db_conf['host'],
                               port=db_conf['port'],
                               user=db_conf['user'],
                               password=db_conf['pwd'],
                               db=db_conf['db'], loop=pool_loop,
                               minsize=1, maxsize=max_connections)


class UserCancelledRequestError(Exception):
    pass


async def middleware_cache(app, handler):
    async def _inner(request):
        request.cache = redis.StrictRedis(connection_pool=redis_conn_pool)

        return await handler(request)

    return _inner


async def middleware_db(app, handler):
    async def _inner(request):
        global db_pool
        global slave_db_pool
        if db_pool is None:
            db_pool = await create_db_pool(db_conf=settings['database_async'])

        async with db_pool.acquire() as main_conn:
            request.db = main_conn
            return await handler(request)

    return _inner
