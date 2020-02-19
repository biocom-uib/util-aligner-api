from json.decoder import JSONDecodeError

from aiohttp import web


@web.middleware
async def sources_api_middleware(request, handler):
    request.sources_api_session = request.app['sources_api_session']
    return await handler(request)


@web.middleware
async def database_middleware(request, handler):
    master_pool = request.app['master_pool']
    async with master_pool.acquire() as master_connection:
        request.db = master_connection
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
