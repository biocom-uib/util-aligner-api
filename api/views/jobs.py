from aiohttp.web import Response
from api.aligner import server_create_job, server_finished_job

async def create_job(request):
    data = await request.json()
    server_create_job.delay(data)
    return Response(body='New job created',
                    status=200)

async def finished_job(request):
    data = await request.json()
    server_finished_job.delay(data)
    return Response(status=200)