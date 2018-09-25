from csv import reader as csv_reader
from io import StringIO
import re


def get_species_id(net):
    try:
        return int(net['species_id'])
    except ValueError:
        return None


def get_network_data(data, input_network=True):
    net = 'net1' if input_network else 'net2'

    if data[net]['edges'] is None:
        data = {
            'species_id': get_species_id(data[net]),
            'score_thresholds': data[net]['score_thresholds'],
            'edges': None
        }
    else:
        try:
            edges = [(int(p1), int(p2)) for p1,p2 in csv_reader(StringIO(data[net]['edges']), delimiter='\t')]
        except ValueError:
            edges = []

        data = {
            'species_id': -1,
            'score_thresholds': {},
            'edges': edges
        }

    return data
