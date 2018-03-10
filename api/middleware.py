import redis

from json.decoder import JSONDecodeError

from aiohttp import web


@web.middleware
async def cache_middleware(request, handler):
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
    redis_pool = request.app['redis_pool']
    request.cache = redis.StrictRedis(connection_pool=redis_pool)
    return await handler(request)


@web.middleware
async def database_middleware(request, handler):
    master_pool = request.app['master_pool']
    slave_pool = request.app['slave_pool']
    async with master_pool.acquire() as master_connection, \
            slave_pool.acquire() as slave_connection:
        request.db = master_connection
        request.slave_db = slave_connection
        return await handler(request)


async def send_errors_sentry(sentry_client, request):
    if sentry_client:  # pragma: nocover
        sentry_client.http_context({
            'url': request.path,
            'query_string': request.query_string,
            'method': request.method,
            'headers': dict(request.headers),
            'cookies': dict(request.cookies),
            'data': await request.read()
        })
        sentry_client.captureException()
        sentry_client.context.clear()


@web.middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)
    except web.HTTPException as e:
        return web.json_response(body=str(e), status=e.status_code)
    except Exception as e:
        await send_errors_sentry(request.app.get('sentry'), request)
        return web.json_response(body=str(e), status=500)


@web.middleware
async def json_middleware(request, handler):
    try:
        request.post_json = {}
        if request.can_read_body:
            request.post_json = await request.json()
    except JSONDecodeError:
        raise web.HTTPBadRequest(reason='"Malformed Json Payload"')
    return await handler(request)
