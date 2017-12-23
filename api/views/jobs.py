from aiohttp.web import Response
import json

async def create_job(request):
    data = await request.json()
    server_create_job(data)
    return Response(body='New job created',
                    status=200)

async def finished_job(request):
    data = await request.json()
    server_finished_job(data)
    return Response(status=200)