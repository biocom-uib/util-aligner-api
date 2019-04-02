import api.v2.views as v2
from config import config

BASE_PATH = config['BASE_PATH']

robots = ['GET', '/util-aligner/robots.txt', v2.robots.robots]

selectors = [
    ['GET', f'{BASE_PATH}/v2/database',              v2.selectors.get_databases],
    ['GET', f'{BASE_PATH}/v2/networks/{{database}}', v2.selectors.get_networks],
    ['GET', f'{BASE_PATH}/v2/aligner',               v2.selectors.get_aligners],

    ['GET', f'{BASE_PATH}/v2/file/{{filename}}',     v2.selectors.get_mongo_file],
]

jobs = [
    ['POST', f'{BASE_PATH}/v2/create-job',          v2.jobs.create_job],
    ['POST', f'{BASE_PATH}/v2/finished-alignment',  v2.jobs.finished_alignment],
    ['POST', f'{BASE_PATH}/v2/finished-comparison', v2.jobs.finished_comparison],
]

routes = [robots] + selectors + jobs
