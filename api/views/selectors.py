from aiohttp.web import Response
import json

from config import get_config

settings = get_config()


async def get_databases(request):
    data = {'data': ['StringDB']}
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
            await mysql_cursor.execute('select species_id, official_name from stringdb_species;')

            species = [f'{official_name} (NCBI: {species_id})'
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
    data = {'data': sorted(['HubAlign', 'AligNet', 'PINALOG', 'SPINAL', 'L-GRAAL'])}
    headers = settings.get('HEADERS')
    return Response(body=json.dumps(data),
                    content_type="application/json",
                    headers=headers,
                    status=200)
