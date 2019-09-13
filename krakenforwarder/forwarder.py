import json
import logging
import time
from typing import Tuple, List, Any

import krakenex
import zmq
from requests import HTTPError
from schema import Schema

from krakenforwarder.util import make_msg, F_KRAKEN_ERROR, F_KRAKEN_LAST, F_KRAKEN_PAIR, F_KRAKEN_RESULT, \
    F_KRAKEN_SINCE, F_KRAKEN_TRADES, F_ASSET_PAIR, F_PULL_PERIOD, F_ZMQ_PUBLISH_PORT, V_INTERNAL_OVER

__all__ = ['KrakenForwarder']


class KrakenForwarder:
    def __init__(self, config: dict):
        Schema({
            F_PULL_PERIOD: int,
            F_ASSET_PAIR: str,
            F_ZMQ_PUBLISH_PORT: int,
        }, ignore_extra_keys=True).validate(config)
        self.__pull_period = config[F_PULL_PERIOD]
        self.__kraken_asset_pair = config[F_ASSET_PAIR]
        self.__zmq_publish_port = config[F_ZMQ_PUBLISH_PORT]
        self.__socket = None  # ZMQ not initiated -> must be initiated in subprocess
        self.__kraken = krakenex.API()
        self.__kraken_since = None
        self.__last_time_done = 0
        self.__logger = logging.getLogger()

        self.__logger.info(
            'core initiated'
            ' with {key_pull_period}={value_pull_period},'
            ' {key_asset_pair}={value_asset_pair}'
            ' and {zmq_publish}={value_zmq_publish}'.format(
                key_pull_period=F_PULL_PERIOD,
                value_pull_period=self.__pull_period,
                key_asset_pair=F_ASSET_PAIR,
                value_asset_pair=self.__kraken_asset_pair,
                zmq_publish=F_ZMQ_PUBLISH_PORT,
                value_zmq_publish=self.__zmq_publish_port,
            )
        )

    def __zmq_init(self) -> None:  # ZMQ has to be called in subprocess
        context = zmq.Context()
        self.__socket = context.socket(zmq.PUB)
        self.__socket.bind('tcp://*:{port}'.format(port=self.__zmq_publish_port))

    def forward(self) -> None:  # this is the core loop
        self.__zmq_init()
        while True:
            current_time = int(time.time())  # current time in seconds

            # wait, eventually
            if current_time % self.__pull_period or current_time == self.__last_time_done:
                time.sleep(0.1)
                continue

            # get recent trades
            try:
                recent_trades, self.__kraken_since = self.__pull_recent_trades()
                self.__last_time_done = current_time
            except (ConnectionError, HTTPError) as error_msg:
                self.__logger.error(error_msg)
                continue

            self.__logger.info('Got {number_of_trades} trades'.format(number_of_trades=len(recent_trades)))
            if len(recent_trades) > 0:
                # broadcast
                for trade in recent_trades:
                    msg = make_msg(
                        pair=self.__kraken_asset_pair,
                        trade_info=trade
                    )
                    self.__socket.send_string(msg)
                self.__socket.send_string(V_INTERNAL_OVER)

    def __pull_recent_trades(self) -> Tuple[List[List[Any]], int]:
        query_result = self.__kraken.query_public(
            F_KRAKEN_TRADES, {
                F_KRAKEN_PAIR: self.__kraken_asset_pair,
                F_KRAKEN_SINCE: self.__kraken_since
            })

        if len(query_result[F_KRAKEN_ERROR]) > 0:
            raise ConnectionError(json.dumps(query_result[F_KRAKEN_ERROR]))

        return query_result[F_KRAKEN_RESULT][self.__kraken_asset_pair], \
            int(query_result[F_KRAKEN_RESULT][F_KRAKEN_LAST])
