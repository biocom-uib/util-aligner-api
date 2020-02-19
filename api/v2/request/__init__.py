from api.v2.request.stringdb import get_network_data as get_stringdb_network_data
from api.v2.request.isobase import get_network_data as get_isobase_network_data
from api.v2.request.stringdbvirus import get_network_data as get_stringdbvirus_network_data
from api.v2.constants import String, IsoBase, StringDBVirus


ADAPTER_DISPATCHER = {
    String: get_stringdb_network_data,
    IsoBase: get_isobase_network_data,
    StringDBVirus: get_stringdbvirus_network_data
}


def get_network_data(data, net_key):
    db = data['db']
    if db not in ADAPTER_DISPATCHER:
        raise NotImplementedError
    return ADAPTER_DISPATCHER[db](data, net_key=net_key)


def adapt_data(raw_data):
    data = {
        'db': raw_data['db'],
        'net1': get_network_data(raw_data, net_key='net1'),
        'net2': get_network_data(raw_data, net_key='net2'),
        'aligners': raw_data['aligner'],
        'aligner_params': raw_data.get('aligner_params', {}),
        'mail': raw_data['mail'],
        'use_cache': raw_data.get('use_cache', True)
    }
    return data
