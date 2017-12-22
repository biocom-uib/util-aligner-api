from aiohttp.web import Response

async def robots(request):
    content = b"User-agent: * \r\nDisallow: / "
    return Response(body=content,
                    content_type="text/plain",
                    status=200)