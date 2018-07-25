from aiohttp.web import Response
from api.aligner import server_create_job, server_finished_job

import re


def fix_stringdb_species_id(data):
    if 'db' in data and data['db'].lower() == 'stringdb':
        data['net1'] = int(re.sub(r'^.*\(NCBI: (\d+)\)$', r'\1', data['net1']))
        data['net2'] = int(re.sub(r'^.*\(NCBI: (\d+)\)$', r'\1', data['net2']))

async def create_job(request):
    data = request.post_json
    fix_stringdb_species_id(data)
    await server_create_job(request.app['master_pool'],
                            request.app['redis_pool'], request.app['celery'],
                            request.app['mongo_db'], data)
    return Response(body='New job created',
                    status=200)


async def finished_job(request):
    data = request.post_json
    fix_stringdb_species_id(data)
    await server_finished_job(request.app['mongo_db'],
                              request.app['redis_pool'], data['job_id'],
                              data['result_id'])
    return Response(status=200)
