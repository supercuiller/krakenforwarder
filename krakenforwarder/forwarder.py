import logging
import time
from typing import Any, Tuple

import krakenex
from json import JSONDecodeError
import requests
import zmq
from requests import HTTPError
from schema import Schema

from krakenforwarder.util import *

__all__ = ['KrakenForwarder']


class KrakenForwarder:
    def __init__(self, config: dict):
        Schema({
            F_PULL_PERIOD: int,
            F_ASSET_PAIR: str,
            F_TYPE: str,
            F_ZMQ_PUBLISH_PORT: int,
        }, ignore_extra_keys=True).validate(config)
        self.__pull_period = config[F_PULL_PERIOD]
        self.__kraken_asset_pair = config[F_ASSET_PAIR]
        self.__kraken_type = config[F_TYPE]
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
        # noinspection PyUnresolvedReferences
        self.__socket = context.socket(zmq.PUB)
        self.__socket.bind('tcp://*:{port}'.format(port=self.__zmq_publish_port))

    def forward(self) -> None:  # this is the core loop
        self.__zmq_init()
        while True:
            current_time = int(time.time())  # current time in seconds
            # wait, eventually
            if current_time % self.__pull_period or current_time == self.__last_time_done:
                time.sleep(0.1)
                # e.g. https://support.kraken.com/hc/en-us/articles/206548367-What-are-the-API-rate-limits-
                continue
            
            # get relevant function
            if self.__kraken_type == V_FUTURES:
                try:
                    get_recent_trades = self.__pull_recent_derv_trades
                except JSONDecodeError as e:
                    self.__logger.warning(f"Cannot decode API result. {str(e)}")
                    continue
            elif self.__kraken_type == V_SPOT:
                get_recent_trades = self.__pull_recent_spot_trades
            else:
                raise ValueError(f"Trade type '{self.__kraken_type}' is unknown.")

            # get recent trades
            try:
                recent_trades, self.__kraken_since = get_recent_trades()
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

    def __pull_recent_spot_trades(self) -> Tuple[List[List[Any]], int]:
        # pull spot from https://api.kraken.com/0/public/Trades
        query_result = self.__kraken.query_public(
            F_SPOT_TRADES, {
                F_PAIR: self.__kraken_asset_pair,
                F_SPOT_SINCE: self.__kraken_since
            })
        if len(query_result[F_SPOT_ERROR]) > 0:
            raise ConnectionError(json.dumps(query_result[F_SPOT_ERROR]))

        return query_result[F_SPOT_RESULT][self.__kraken_asset_pair], \
            int(query_result[F_SPOT_RESULT][F_SPOT_LAST])

    def __pull_recent_derv_trades(self) -> Tuple[List[List[Any]], int]:
        # sample call for futures
        # https://futures.kraken.com/derivatives/api/v3/history?symbol=pi_xbtusd&lastTime=2019-02-14T09:31:26.027Z
        asset_pair = self.__kraken_asset_pair

        url = f"""{F_DERV_URL_ROOT}{F_DERV_HISTORY}?{F_DERV_SYMBOL}={asset_pair}"""

        # GET request
        query_result = requests.get(url).json()
        if query_result[F_DERV_RESULT] != F_DERV_SUCCESS:
            raise ConnectionError(json.dumps(query_result[F_DERV_HISTORY]))

        # filter out all trades that happened before self.__kraken_since
        if self.__kraken_since is not None:
            query_result[F_DERV_HISTORY] = [
                trade for trade in query_result[F_DERV_HISTORY] if trade[F_DERV_TIME] > self.__kraken_since
            ]

        if len(query_result[F_DERV_HISTORY]) > 0:
            kraken_since = max([trade[F_DERV_TIME] for trade in query_result[F_DERV_HISTORY]])
        else:
            kraken_since = self.__kraken_since
        return query_result[F_DERV_HISTORY], kraken_since
