import api.v2.views as v2
from config import config

BASE_PATH = config['BASE_PATH']

robots = ['GET', '/util-aligner/robots.txt', v2.robots.robots]

selectors = [
    ['GET', f'{BASE_PATH}/v2/database',                 v2.selectors.get_databases],
    ['GET', f'{BASE_PATH}/v2/networks/{{db}}',          v2.selectors.get_networks],
    ['GET', f'{BASE_PATH}/v2/aligner',                  v2.selectors.get_aligners],

    ['POST', f'{BASE_PATH}/v2/species/{{db}}/select',    v2.selectors.get_species],
    ['POST', f'{BASE_PATH}/v2/proteins/{{db}}/select',   v2.selectors.get_proteins],
    ['POST', f'{BASE_PATH}/v2/networks/{{db}}/select',   v2.selectors.get_network],
    ['GET',  f'{BASE_PATH}/v2/networks/{{db}}/weighted', v2.selectors.get_weighted_network],

    ['GET', f'{BASE_PATH}/v2/file/{{filename}}',        v2.selectors.get_mongo_file],
    ['GET', f'{BASE_PATH}/v2/alignment/{{result_id}}',  v2.selectors.get_mongo_alignment],
    ['GET', f'{BASE_PATH}/v2/comparison/{{result_id}}', v2.selectors.get_mongo_comparison],
]

jobs = [
    ['GET',  f'{BASE_PATH}/v2/status',                  v2.jobs.status],
    ['POST', f'{BASE_PATH}/v2/create-job',              v2.jobs.create_job],
    ['POST', f'{BASE_PATH}/v2/finished-alignment',      v2.jobs.finished_alignment],
    ['POST', f'{BASE_PATH}/v2/finished-comparison',     v2.jobs.finished_comparison],
]

routes = [robots] + selectors + jobs
