import api.v1.views as v1
import api.v2.views as v2
from config import config

BASE_PATH = config['BASE_PATH']

robots = ['GET', '/util-aligner/robots.txt', v1.robots.robots]

selectors = [
    ['GET', f'{BASE_PATH}/v1/database',              v1.selectors.get_databases],
    ['GET', f'{BASE_PATH}/v1/networks/{{database}}', v1.selectors.get_networks],
    ['GET', f'{BASE_PATH}/v1/aligner',               v1.selectors.get_aligners],

    ['GET', f'{BASE_PATH}/v2/database',              v2.selectors.get_databases],
    ['GET', f'{BASE_PATH}/v2/networks/{{database}}', v2.selectors.get_networks],
    ['GET', f'{BASE_PATH}/v2/aligner',               v2.selectors.get_aligners],

    ['GET', f'{BASE_PATH}/v2/file/{{filename}}',     v2.selectors.get_mongo_file],
]

jobs = [
    ['POST', f'{BASE_PATH}/v1/create-job',   v1.jobs.create_job],
    ['POST', f'{BASE_PATH}/v1/finished-job', v1.jobs.finished_job],

    ['POST', f'{BASE_PATH}/v2/create-job',   v2.jobs.create_job],
    ['POST', f'{BASE_PATH}/v2/finished-job', v2.jobs.finished_job],
]

routes = [robots] + selectors + jobs
