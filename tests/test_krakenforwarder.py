import time
from multiprocessing import Process

from krakenforwarder.forwarder import KrakenForwarder
from krakenforwarder.listener import listen
from krakenforwarder.util import *


def test_krakenforwarder():
    cfg_forwarders = [
        {
            F_PULL_PERIOD: 5,  # in seconds
            F_ASSET_PAIR: 'XXBTZEUR',  # see kraken.com API documentation for available values
            F_TYPE: V_SPOT,
            F_ZMQ_PUBLISH_PORT: 5555
        },
        {
            F_PULL_PERIOD: 5,  # in seconds
            F_ASSET_PAIR: 'XETHZEUR',  # see kraken.com API documentation for available values
            F_TYPE: V_SPOT,
            F_ZMQ_PUBLISH_PORT: 5556
        },
        {
            F_PULL_PERIOD: 5,  # in seconds
            F_ASSET_PAIR: 'pi_xbtusd',
            F_TYPE: V_FUTURES,
            # see https://support.kraken.com/hc/en-us/articles/360022839531-Tickers for possible choices
            F_ZMQ_PUBLISH_PORT: 5557
        },
    ]

    cfg_listener = {
        F_KEY_ZMQ_HOSTNAME: 'localhost',
        F_ZMQ_PUBLISH_PORT: [cfg[F_ZMQ_PUBLISH_PORT] for cfg in cfg_forwarders]
    }

    proc_forwarders = []
    for cfg in cfg_forwarders:
        kraken_forwarder = KrakenForwarder(cfg)
        forward_process = Process(target=kraken_forwarder.forward)
        proc_forwarders.append(forward_process)

    for proc in proc_forwarders:
        proc.start()

    time.sleep(1)

    for msg in listen(cfg_listener):
        print(msg)

    for proc in proc_forwarders:
        proc.join()


if __name__ == '__main__':
    test_krakenforwarder()
