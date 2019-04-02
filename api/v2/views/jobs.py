from aiohttp.web import Response
import json

import api.aligner as aligner
from api.v2.request import adapt_data

from config import get_config

settings = get_config()


async def create_job(request):
    data = request.post_json
    data = adapt_data(data)
    job_id = await aligner.server_create_alignment_job_group(
            request.app['redis_pool'], request.app['celery'],
            request.app['mongo_db'], request.app['mongo_gridfs'], data)

    headers = settings.get('HEADERS')
    return Response(body=json.dumps({'job_id': job_id}),
                    content_type='application/json',
                    headers=headers,
                    status=200)


async def status(request):
    job_id = request.rel_url.query['job_id']
    cache_connection = request.app['redis_pool']

    result = await aligner.get_job_result_id(cache_connection, job_id)

    if result is not None:
        resp_data = {'result': result}

    else:
        group_status = await aligner.get_job_group_status(cache_connection, job_id)
        resp_data = group_status if group_status['njobs'] > 0 else {}

    headers = settings.get('HEADERS')
    return Response(body=json.dumps(resp_data),
                    content_type='application/json',
                    headers=headers,
                    status=200)


async def finished_alignment(request):
    data = request.post_json
    await aligner.server_finished_alignment(request.app['mongo_db'], request.app['mongo_gridfs'],
                              request.app['redis_pool'], request.app['celery'],
                              data['job_id'], data['result_id'])
    return Response(status=200)


async def finished_comparison(request):
    data = request.post_json
    await aligner.server_finished_comparison(request.app['mongo_db'], request.app['mongo_gridfs'],
                                       request.app['redis_pool'], data['job_id'],
                                       data['result_id'])
    return Response(status=200)
