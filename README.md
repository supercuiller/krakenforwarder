# krakenforwarder
This Python program listens to trades from Crypto-exchange platform Kraken (https://www.kraken.com) and forwards them on a TCP port so you can plug in anything, like a live algorithmic trader or a live analysis tool.

## Installation

```pip3 install krakenforwarder``` 

## Usage

Launch the forwarder in sub-process, then listen

```python
import time
from multiprocessing import Process

from krakenforwarder.forwarder import KrakenForwarder
from krakenforwarder.listener import listen
from krakenforwarder.util import *

cfg_forwarders = [
    {
        F_PULL_PERIOD: 5,  # in seconds
        F_ASSET_PAIR: 'XXBTZEUR',  # see https://support.kraken.com/hc/en-us/articles/360000920306-Ticker-pairs
        F_TYPE: V_SPOT,
        F_ZMQ_PUBLISH_PORT: 5555
    },
    {
        F_PULL_PERIOD: 5,  # in seconds
        F_ASSET_PAIR: 'XETHZEUR',  # see https://support.kraken.com/hc/en-us/articles/360000920306-Ticker-pairs
        F_TYPE: V_SPOT,
        F_ZMQ_PUBLISH_PORT: 5556
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
```

This prints trades in console:

```
{"pair": "XXBTZEUR", "Trade": ["9388.90000", "0.01604115", 1568346002.9574, "b", "m", ""]}
{"pair": "XXBTZEUR", "Trade": ["9390.00000", "0.03569491", 1568346002.9981, "b", "m", ""]}
{"pair": "XXBTZEUR", "Trade": ["9390.00000", "0.01000000", 1568346003.0047, "b", "m", ""]}
{"pair": "XXBTZEUR", "Trade": ["9392.90000", "0.03477392", 1568346003.0213, "b", "m", ""]}
OVER
...
{"pair": "XXBTZEUR", "Trade": ["9384.50000", "0.00500000", 1568346015.5326, "s", "m", ""]}
OVER
{"pair": "XETHZEUR", "Trade": ["162.98000", "0.24458271", 1568346014.6035, "s", "m", ""]}
{"pair": "XETHZEUR", "Trade": ["162.98000", "0.00063427", 1568346014.6274, "s", "m", ""]}
{"pair": "XETHZEUR", "Trade": ["162.98000", "0.00000165", 1568346014.6296, "s", "m", ""]}
OVER

```

To call forward contracts, instead use

```python
from krakenforwarder.util import *
cfg_forwarders = [
    {
        F_PULL_PERIOD: 5,  # in seconds
        F_ASSET_PAIR: 'pi_xbtusd',
        F_TYPE: V_FUTURES,
        # see https://support.kraken.com/hc/en-us/articles/360022839531-Tickers for possible choices
        F_ZMQ_PUBLISH_PORT: 5557
    },
]
```