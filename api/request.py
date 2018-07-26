import re


ADAPTER_DISPATCHER = {
    'stringDB': get_stringdb_network_data
}
PERSONALIZED_NETWORK = 'Personalized Network'


def get_stringdb_species_id(net):
    try:
        return int(re.sub(r'^.*\(NCBI: (\d+)\)$', r'\1', net))
    except ValueError:
        return -1

def get_scores(thresholds, input_network=True):
    net = 'net1' if input_network else 'net2'
    scores = {
        re.sub(f'{net}_', r'\1', score): threshold 
        for score, threshold in thresholds.items()
        if score.startswith(net)
    }
    return scores


def get_stringdb_network_data(net, edges, input_network=True):
    data = {
        'species_id': get_stringdb_species_id(net),
        'score_thresholds': get_scores(data['score_thresholds'], input_network=input_network),
        'edges': edges
    }
    return data


def get_network_data(net, edges, db, input_network=True):
    if db not in ADAPTER_DISPATCHER:
        raise NotImplementedError
    return ADAPTER_DISPATCHER[db](net, edges, input_network=True)


def adapt_data(raw_data):
    data = {
        'db': raw_data['db'],
        'net1': get_network_data(raw_data['net1'], raw_data.get('edges', [])    , raw_data['db'])
        'net2': get_network_data(raw_data['net2'], raw_data.get('edges', []), raw_data['db'], input_network=False)
    }
    return data
