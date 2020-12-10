import json
import logging
import time
import datetime
from dateutil import tz
import dateutil.parser
from typing import Any, List, Tuple

import krakenex
import requests
import zmq
from requests import HTTPError
from schema import Schema

from krakenforwarder.util import (F_ASSET_PAIR, F_DERV_FLAG, F_DERV_HISTORY,
                                  F_DERV_SERVER_TIME, F_DERV_SYMBOL,
                                  F_DERV_URL_ROOT, F_KRAKEN_ERROR,
                                  F_KRAKEN_LAST, F_KRAKEN_PAIR,
                                  F_KRAKEN_RESULT, F_KRAKEN_SINCE,
                                  F_KRAKEN_TRADES, F_PULL_PERIOD, F_RESULT,
                                  F_SUCCESS, F_ZMQ_PUBLISH_PORT,
                                  V_INTERNAL_OVER, make_msg)

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
                time.sleep(0.1) # need to check rate limit, 
                # e.g. https://support.kraken.com/hc/en-us/articles/206548367-What-are-the-API-rate-limits-
                continue
            
            # get relevant function
            if F_DERV_FLAG in self.__kraken_asset_pair:
                get_recent_trades = self.__pull_recent_derv_trades
            else:
                get_recent_trades = self.__pull_recent_trades 

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

    def __pull_recent_trades(self) -> Tuple[List[List[Any]], int]:

        # pull spot from https://api.kraken.com/0/public/Trades
        query_result = self.__kraken.query_public(
            F_KRAKEN_TRADES, {
                F_KRAKEN_PAIR: self.__kraken_asset_pair,
                F_KRAKEN_SINCE: self.__kraken_since
            })
        if len(query_result[F_KRAKEN_ERROR]) > 0:
            raise ConnectionError(json.dumps(query_result[F_KRAKEN_ERROR]))

        return query_result[F_KRAKEN_RESULT][self.__kraken_asset_pair], \
            int(query_result[F_KRAKEN_RESULT][F_KRAKEN_LAST])

    def __pull_recent_derv_trades(self)->Tuple[List[List[Any]], int]:

        # sample call for futures
        # https://futures.kraken.com/derivatives/api/v3/history?symbol=pi_xbtusd&lastTime=2019-02-14T09:31:26.027Z
        asset_pair = self.__kraken_asset_pair
        url = F_DERV_URL_ROOT + F_DERV_HISTORY + F_DERV_SYMBOL + asset_pair
        
        # GET request
        query_result = requests.get(url).json()
        if query_result[F_RESULT] != F_SUCCESS:
            raise ConnectionError(json.dumps(query_result[F_DERV_HISTORY]))

        # deal with conversion from zulu time
        server_time = query_result[F_DERV_SERVER_TIME]
        utc_time = dateutil.parser.isoparse(server_time)

        # hack: hard-coded start of Unix epoch
        epoch_start = datetime.datetime(1970,1,1,tzinfo=tz.tzutc())
        secs = int((utc_time - epoch_start).total_seconds())
        return query_result[F_DERV_HISTORY], secs