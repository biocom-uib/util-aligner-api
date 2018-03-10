from api.views import robots, selectors, jobs
robots = ['GET', '/util-aligner/robots.txt', robots.robots]

selectors = [
    ['GET', '/util-aligner/database', selectors.get_databases],
    ['GET', '/util-aligner/networks/{database}', selectors.get_networks],
    ['GET', '/util-aligner/aligner', selectors.get_aligners],
]

jobs = [
    ['POST', '/util-aligner/create-job', jobs.create_job],
]

routes = [robots] + selectors + jobs
