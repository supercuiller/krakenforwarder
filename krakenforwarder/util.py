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
