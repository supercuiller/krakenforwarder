import json
from typing import List


F_KRAKEN_ERROR = 'error'
F_KRAKEN_LAST = 'last'
F_KRAKEN_PAIR = 'pair'
F_KRAKEN_RESULT = 'result'
F_KRAKEN_SINCE = 'since'
F_KRAKEN_TRADES = 'Trades'
F_ASSET_PAIR = 'Asset Pair'
F_PULL_PERIOD = 'Pull Period'
F_TRADE = 'Trade'
F_ZMQ_PUBLISH_PORT = 'Publish Port'
F_KEY_ZMQ_HOSTNAME = 'Hostname'
V_INTERNAL_OVER = 'OVER'

F_DERV_FLAG = '_'
F_RESULT = 'result'
F_SUCCESS = 'success'
F_DERV_URL_ROOT = 'https://futures.kraken.com/derivatives/api/v3/'
F_DERV_HISTORY = 'history'
F_DERV_ORDERS = 'orderbook'
F_DERV_SYMBOL = '?symbol='
F_DERV_LAST_TIME = '&lastTime='
F_DERV_SERVER_TIME = 'serverTime'


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
        F_KRAKEN_PAIR: pair,
        F_TRADE: trade_info,
    })
