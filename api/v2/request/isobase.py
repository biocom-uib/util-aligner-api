
def get_network_data(data, input_network=True):
    net = 'net1' if input_network else 'net2'

    return data[net]
