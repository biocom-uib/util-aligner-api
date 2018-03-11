from aiohttp.web import Response
import json

from config import get_config

settings = get_config()


async def get_databases(request):
    data = {'data': ['IsoBase']}
    headers = settings.get('HEADERS')
    return Response(body=json.dumps(data),
                    content_type="application/json",
                    headers=headers,
                    status=200)


async def get_networks(request):
    data = {'data': ['cel', 'dme', 'sce', 'hsa', 'mus']}
    headers = settings.get('HEADERS')
    return Response(body=json.dumps(data),
                    content_type="application/json",
                    headers=headers,
                    status=200)


async def get_aligners(request):
    data = {'data': ['AligNet', 'Pinalog', 'Spinal']}
    headers = settings.get('HEADERS')
    return Response(body=json.dumps(data),
                    content_type="application/json",
                    headers=headers,
                    status=200)
