import json
import logging
import time
from typing import Tuple, List, Any

import krakenex
import zmq
from requests import HTTPError
from schema import Schema

from krakenforwarder.util import FORMAT_INTERNAL_ZMQ_PUBLISH_TRADE, KEY_KRAKEN_ASSET_PAIR, KEY_KRAKEN_ERROR, \
    KEY_KRAKEN_LAST, \
    KEY_KRAKEN_PAIR, KEY_KRAKEN_RESULT, KEY_KRAKEN_SINCE, KEY_KRAKEN_TRADES, KEY_PULL_PERIOD, KEY_ZMQ_PUBLISH_PORT, \
    VALUE_INTERNAL_OVER, VALUE_INTERNAL_TRADE

__all__ = ['KrakenForwarder']


class KrakenForwarder:
    def __init__(self, config: dict):
        Schema({
            KEY_PULL_PERIOD: int,
            KEY_KRAKEN_ASSET_PAIR: str,
            KEY_ZMQ_PUBLISH_PORT: int,
        }, ignore_extra_keys=True).validate(config)
        self.__pull_period = config[KEY_PULL_PERIOD]
        self.__kraken_asset_pair = config[KEY_KRAKEN_ASSET_PAIR]
        self.__zmq_publish_port = config[KEY_ZMQ_PUBLISH_PORT]
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
                key_pull_period=KEY_PULL_PERIOD,
                value_pull_period=self.__pull_period,
                key_asset_pair=KEY_KRAKEN_ASSET_PAIR,
                value_asset_pair=self.__kraken_asset_pair,
                zmq_publish=KEY_ZMQ_PUBLISH_PORT,
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
                    msg = FORMAT_INTERNAL_ZMQ_PUBLISH_TRADE.format(
                        label=VALUE_INTERNAL_TRADE,
                        pair=self.__kraken_asset_pair,
                        trade_info=trade
                    )
                    self.__socket.send_string(msg)
                self.__socket.send_string(VALUE_INTERNAL_OVER)

    def __pull_recent_trades(self) -> Tuple[List[List[Any]], int]:
        query_result = self.__kraken.query_public(
            KEY_KRAKEN_TRADES, {
                KEY_KRAKEN_PAIR: self.__kraken_asset_pair,
                KEY_KRAKEN_SINCE: self.__kraken_since
            })

        if len(query_result[KEY_KRAKEN_ERROR]) > 0:
            raise ConnectionError(json.dumps(query_result[KEY_KRAKEN_ERROR]))

        return query_result[KEY_KRAKEN_RESULT][self.__kraken_asset_pair], \
               int(query_result[KEY_KRAKEN_RESULT][KEY_KRAKEN_LAST])
