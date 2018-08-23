import zmq

from krakenforwarder.util import KEY_ZMQ_PUBLISH_PORT, KEY_ZMQ_HOSTNAME

__all__ = ['listen']


def listen(config: dict):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect('tcp://{zmq_host}:{zmq_port}'.format(
        zmq_host=config[KEY_ZMQ_HOSTNAME],
        zmq_port=config[KEY_ZMQ_PUBLISH_PORT])
    )
    socket.setsockopt_string(zmq.SUBSCRIBE, '')
    while True:
        msg = socket.recv_string()
        yield msg
