from api.views import robots, selectors
robots = ['GET', '/robots.txt', robots.robots]
selectors = [
    ['GET', '/database', selectors.get_databases],
    ['GET', '/networks/{database}', selectors.get_networks],
    ['GET', '/aligner', selectors.get_aligners],
]


routes = [robots] + selectors