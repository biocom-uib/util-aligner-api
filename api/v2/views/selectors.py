from aiohttp.web import Response
from bson.json_util import dumps as bson_dumps, RELAXED_JSON_OPTIONS
from bson.objectid import ObjectId
import json
import re

from motor.aiohttp import AIOHTTPGridFS

from config import get_config

settings = get_config()


async def get_databases(request):
    data = {'data': [{'text': 'StringDB', 'value': 'stringdb'}]}
    headers = settings.get('HEADERS')
    return Response(body=json.dumps(data),
                    content_type="application/json",
                    headers=headers,
                    status=200)


async def get_networks(request):
    mysql_conn = request.db

    db_name = request.match_info['database']

    if db_name.lower() == 'stringdb':
        async with mysql_conn.cursor() as mysql_cursor:
            await mysql_cursor.execute('select species_id, official_name from stringdb_species order by official_name;')

            species = [{'text':f'{official_name} (NCBI: {species_id})', 'value': species_id}
                        for species_id, official_name in await mysql_cursor.fetchall()]

        data = {'data': species}
    else:
        data = {'data': []}

    headers = settings.get('HEADERS')
    return Response(body=json.dumps(data),
                    content_type="application/json",
                    headers=headers,
                    status=200)


async def get_aligners(request):
    data = {
        'data':
            [{'text': a, 'value': a.lower()}
                for a in sorted(['HubAlign', 'AligNet', 'PINALOG', 'SPINAL', 'L-GRAAL'])]
    }

    headers = settings.get('HEADERS')
    return Response(body=json.dumps(data),
                    content_type="application/json",
                    headers=headers,
                    status=200)


async def get_mongo_alignment(request):
    obj_id = request.match_info['result_id']
    res = await request.app['mongo_db'].alignments.find_one({'_id': ObjectId(obj_id)})

    headers = settings.get('HEADERS')
    return Response(body=bson_dumps(res, json_options=RELAXED_JSON_OPTIONS),
                    content_type="application/json",
                    headers=headers,
                    status=200)


async def get_mongo_comparison(request):
    obj_id = request.match_info['result_id']
    res = await request.app['mongo_db'].comparisons.find_one({'_id': ObjectId(obj_id)})

    headers = settings.get('HEADERS')
    return Response(body=bson_dumps(res, json_options=RELAXED_JSON_OPTIONS),
                    content_type="application/json",
                    headers=headers,
                    status=200)


class GetMongoFileHandler(AIOHTTPGridFS):
    def __init__(self):
        pass

    def _get_gridfs_file(self, bucket, filename, request):
        return bucket.open_download_stream(file_id = ObjectId(filename))

    def _get_cache_time(self, filename, modified, mime_type):
        return 0

    def _set_extra_headers(self, response, gridout):
        response.headers['Content-Disposition'] = 'attachment; filename="' + re.sub(r'^(.*)_(.*?)$', r'\1.\2', gridout.filename) + '"'

    def _init_base(self, request):
        self._database = request.app['mongo_db']
        self._bucket = request.app['mongo_gridfs']
        self._get_gridfs_file = self._get_gridfs_file
        self._get_cache_time = self._get_cache_time
        self._set_extra_headers = self._set_extra_headers

    async def __call__(self, request):
        self._init_base(request)
        return await super().__call__(request)

get_mongo_file = GetMongoFileHandler()

# async def get_mongo_file(request):
#     mongodb = request.app['mongo_db']
#     mongo_gridfs = request.app['mongo_gridfs']
#
#     handler = AIOHTTPGridFS(mongodb, get_gridfs_file=get_gridfs_file_by_id)
#
#     response = await handler(request)
#     return response
#
