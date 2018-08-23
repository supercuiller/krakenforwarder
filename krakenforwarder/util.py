from typing import List


def merge_dicts(dics: List[dict]) -> dict:
    """
    Merges a list of dict objects to one dict object
    """
    merged = dict()
    for dic in dics:
        merged.update(dic)
    return merged


FORMAT_INTERNAL_ZMQ_PUBLISH_TRADE = '{label}::{pair}::{trade_info}'
KEY_KRAKEN_ASSET_PAIR = 'Asset Pair'
KEY_KRAKEN_ERROR = 'error'
KEY_KRAKEN_LAST = 'last'
KEY_KRAKEN_PAIR = 'pair'
KEY_KRAKEN_RESULT = 'result'
KEY_KRAKEN_SINCE = 'since'
KEY_KRAKEN_TRADES = 'Trades'
KEY_PULL_PERIOD = 'Pull Period'
KEY_ZMQ_PUBLISH_PORT = 'Publish Port'
KEY_ZMQ_HOSTNAME = 'Hostname'
VALUE_INTERNAL_OVER = 'OVER'
VALUE_INTERNAL_TRADE = 'TRADE'
