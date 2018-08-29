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

# configure forwarder
config_forwarder = {
    'Pull Period': 5,  # in seconds
    'Asset Pair': 'XXBTZEUR',  # see kraken.com API documentation for available values
    'Publish Port': 5555
}

# configure listener
config_listener = {
    'Hostname': 'localhost',
    'Publish Port': 5555  # must be same port as in forwarder config
}

kraken_forwarder = KrakenForwarder(config_forwarder)
forward_process = Process(target=kraken_forwarder.forward)
forward_process.start()

time.sleep(1)
for msg in listen(config_listener):  # infinite loop
    print(msg)  # do stuff

forward_process.join()  # is never reached but enables debug
```

This prints trades in console:

```
TRADE::XXBTZEUR::['5564.00000', '0.00156837', 1534701743.7647, 'b', 'l', '']
TRADE::XXBTZEUR::['5567.20000', '0.00302475', 1534701826.8837, 'b', 'l', '']
TRADE::XXBTZEUR::['5567.20000', '0.00265558', 1534701840.5956, 'b', 'l', '']
...
TRADE::XXBTZEUR::['5578.40000', '0.02944100', 1534709441.8448, 'b', 'l', '']
OVER
TRADE::XXBTZEUR::['5578.10000', '0.26489984', 1534709451.152, 's', 'l', '']
TRADE::XXBTZEUR::['5578.10000', '0.81510016', 1534709451.1716, 's', 'l', '']
OVER
TRADE::XXBTZEUR::['5578.20000', '0.00494538', 1534709461.3898, 'b', 'm', '']
TRADE::XXBTZEUR::['5578.00000', '0.28809346', 1534709464.4693, 's', 'm', '']
OVER
```
