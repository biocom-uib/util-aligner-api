from api.views import robots, selectors, jobs
from config import config

BASE_PATH = config['BASE_PATH']

robots = ['GET', '/util-aligner/robots.txt', robots.robots]

selectors = [
    ['GET', f'{BASE_PATH}/database',                 selectors.get_databases],
    ['GET', f'{BASE_PATH}/networks/{{database}}',    selectors.get_networks],
    ['GET', f'{BASE_PATH}/aligner',                  selectors.get_aligners],

    ['GET', f'{BASE_PATH}/file/{{filename}}',        selectors2.get_mongo_file],
]

jobs = [
    ['POST', f'{BASE_PATH}/create-job',      jobs.create_job],
    ['POST', f'{BASE_PATH}/finished-job',    jobs.finished_job],
]

routes = [robots] + selectors + jobs
