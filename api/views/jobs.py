from aiohttp.web import Response
from api.aligner import server_create_job, server_finished_job


async def create_job(request):
    data = request.post_json
    await server_create_job(request.app['master_pool'],
                            request.app['redis_pool'], request.app['celery'],
                            data)
    return Response(body='New job created',
                    status=200)


async def finished_job(request):
    data = request.post_json
    await server_finished_job(request.app['master_pool'],
                              request.app['redis_pool'], data['job_id'])
    return Response(status=200)
