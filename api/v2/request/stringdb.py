from csv import reader as csv_reader
from io import StringIO
import re


def get_species_id(net_desc):
    try:
        return int(net_desc['species_id'])
    except ValueError:
        return None


def get_network_data(data, net_key):
    if data[net_key]['edges'] is None:
        data = {
            'species_id': get_species_id(data[net_key]),
            'score_thresholds': data[net_key]['score_thresholds'],
            'edges': None
        }
    else:
        try:
            edges = [(int(p1), int(p2)) for p1,p2 in csv_reader(StringIO(data[net_key]['edges']), delimiter='\t')]
        except ValueError:
            edges = []

        data = {
            'species_id': -1,
            'score_thresholds': {},
            'edges': edges
        }

    return data
