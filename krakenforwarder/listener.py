import zmq

from krakenforwarder.util import F_ZMQ_PUBLISH_PORT, F_KEY_ZMQ_HOSTNAME

__all__ = ['listen']


def listen(config: dict):
    context = zmq.Context()
    # noinspection PyUnresolvedReferences
    socket = context.socket(zmq.SUB)
    for port in config[F_ZMQ_PUBLISH_PORT]:
        socket.connect('tcp://{zmq_host}:{zmq_port}'.format(zmq_host=config[F_KEY_ZMQ_HOSTNAME], zmq_port=port))
    # noinspection PyUnresolvedReferences
    socket.setsockopt_string(zmq.SUBSCRIBE, '')
    while True:
        msg = socket.recv_string()
        yield msg
