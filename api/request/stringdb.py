from csv import reader as csv_reader
from io import StringIO
import re

from api.constants import PERSONALIZED_NETWORK


def get_species_id(net):
    if net == PERSONALIZED_NETWORK:
        return -1
    try:
        return int(re.sub(r'^.*\(NCBI: (\d+)\)$', r'\1', net))
    except ValueError:
        return -1


def get_scores(thresholds, input_network=True):
    net = 'range_net_1_' if input_network else 'range_net_2_'
    scores = {
        score[len(net):]: int(threshold)
        for score, threshold in thresholds.items()
        if score.startswith(net)
    }
    return scores


def get_network_data(data, input_network=True):
    net = 'net1' if input_network else 'net2'
    edges_key = 'proteins_1' if input_network else 'proteins_2'

    edges = [(int(p1), int(p2)) for p1,p2 in csv_reader(StringIO(data.get(edges_key, "")), delimiter='\t')]

    data = {
        'species_id': get_species_id(data[net]),
        'score_thresholds': get_scores(data['scores_net'], input_network=input_network),
        'edges': edges
    }

    return data
