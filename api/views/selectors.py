from aiohttp.web import Response
import json


async def get_databases(request):
    data = {'data': ['IsoBase']}
    return Response(body=json.dumps(data),
                    content_type="application/json",
                    headers={'Access-Control-Allow-Origin': 'biocom.uib.es/~adria/'},
                    status=200)


async def get_networks(request):
    data = {'data': ['cel', 'dme', 'sce', 'hsa', 'mus']}
    return Response(body=json.dumps(data),
                    content_type="application/json",
                    headers={'Access-Control-Allow-Origin': 'biocom.uib.es/~adria/'},
                    status=200)


async def get_aligners(request):
    data = {'data': ['AligNet', 'Pinalog', 'Spinal']}
    return Response(body=json.dumps(data),
                    content_type="application/json",
                    headers={'Access-Control-Allow-Origin': 'biocom.uib.es/~adria/'},
                    status=200)
