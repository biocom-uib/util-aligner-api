from aiohttp.web import Response
from api.aligner import server_create_job, server_finished_job


async def create_job(request):
    data = request.post_json
    server_create_job(data, request.app['celery'])
    return Response(body='New job created',
                    status=200)


async def finished_job(request):
    data = request.post_json
    server_finished_job(data)
    return Response(status=200)
