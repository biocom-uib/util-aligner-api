from aiohttp.web import Response
from api.aligner import server_create_job, server_finished_job
from api.v1.request import adapt_data


async def create_job(request):
    data = request.post_json
    data = adapt_data(data)
    await server_create_job(request.app['master_pool'],
                            request.app['redis_pool'], request.app['celery'],
                            request.app['mongo_db'], request.app['mongo_gridfs'],
                            data)
    return Response(body='New job created',
                    status=200)


async def finished_job(request):
    data = request.post_json
    await server_finished_job(request.app['mongo_db'], request.app['mongo_gridfs'],
                              request.app['redis_pool'], data['job_id'],
                              data['result_id'])
    return Response(status=200)
