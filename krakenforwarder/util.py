import json
from typing import List

F_ASSET_PAIR = 'Asset Pair'
F_DERV_HISTORY = 'history'
F_DERV_LAST_TIME = 'lastTime'
F_DERV_ORDERS = 'orderbook'
F_DERV_RESULT = 'result'
F_DERV_SERVER_TIME = 'serverTime'
F_DERV_SUCCESS = 'success'
F_DERV_SYMBOL = 'symbol'
F_DERV_TIME = 'time'
F_DERV_URL_ROOT = 'https://futures.kraken.com/derivatives/api/v3/'
F_KEY_ZMQ_HOSTNAME = 'Hostname'
F_PAIR = 'pair'
F_PULL_PERIOD = 'Pull Period'
F_SPOT_ERROR = 'error'
F_SPOT_LAST = 'last'
F_SPOT_RESULT = 'result'
F_SPOT_SINCE = 'since'
F_SPOT_TRADES = 'Trades'
F_TRADE = 'Trade'
F_TYPE = 'type'
F_ZMQ_PUBLISH_PORT = 'Publish Port'
V_FUTURES = 'futures'
V_INTERNAL_OVER = 'OVER'
V_SPOT = 'spot'


def merge_dicts(dics: List[dict]) -> dict:
    """
    Merges a list of dict objects to one dict object
    """
    merged = dict()
    for dic in dics:
        merged.update(dic)
    return merged


def make_msg(pair: str, trade_info: list) -> str:
    return json.dumps({
        F_PAIR: pair,
        F_TRADE: trade_info,
    })
