import time

from multiprocessing import Process

from krakenforwarder.forwarder import KrakenForwarder
from krakenforwarder.listener import listen


def test_krakenforwarder():
    config_forwarder = {
        'Pull Period': 5,  # in seconds
        'Asset Pair': 'XXBTZEUR',  # see kraken.com API documentation for available values
        'Publish Port': 5555
    }
    config_listener = {
        'Hostname': 'localhost',
        'Publish Port': 5555  # must be same port as for core
    }
    kraken_forwarder = KrakenForwarder(config_forwarder)
    forward_process = Process(target=kraken_forwarder.forward)
    forward_process.start()

    time.sleep(1)

    for msg in listen(config_listener):
        print(msg)

    forward_process.join()


if __name__ == '__main__':
    test_krakenforwarder()
