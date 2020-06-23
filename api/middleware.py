from json.decoder import JSONDecodeError

from aiohttp import web


@web.middleware
async def sources_api_middleware(request, handler):
    request.sources_api_session = request.app['sources_api_session']
    return await handler(request)


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
