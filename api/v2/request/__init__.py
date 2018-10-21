from api.v2.request.stringdb import get_network_data as get_stringdb_network_data
from api.v2.constants import String


ADAPTER_DISPATCHER = {
    String: get_stringdb_network_data
}


def get_network_data(data, input_network=True):
    db = data['db']
    if db not in ADAPTER_DISPATCHER:
        raise NotImplementedError
    return ADAPTER_DISPATCHER[db](data, input_network=input_network)


def adapt_data(raw_data):
    data = {
        'db': raw_data['db'],
        'net1': get_network_data(raw_data),
        'net2': get_network_data(raw_data, input_network=False),
        'aligners': raw_data['aligner'],
        'aligner_params': raw_data.get('aligner_params', {}),
        'mail': raw_data['mail'],
    }
    return data
