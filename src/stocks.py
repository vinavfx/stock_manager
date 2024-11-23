# -----------------------------------------------------------
# AUTHOR --------> Francisco Contreras
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
import os
import sys
from ..python_util.util import jread
from ..env import INDEXING_DIR

stocks_data = {}


def load_data():
    global stocks_data
    stocks_data = jread(os.path.join(INDEXING_DIR, 'stocks.json'))

    if sys.version_info[0] < 3:
        stocks_data = convert_to_utf8(stocks_data)


def get_stocks():
    return stocks_data


def convert_to_utf8(data):
    if isinstance(data, dict):
        return {convert_to_utf8(key): convert_to_utf8(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_utf8(element) for element in data]
    elif isinstance(data, str):
        return data.encode('utf-8') if sys.version_info[0] < 3 else data
    elif sys.version_info[0] < 3 and isinstance(data, unicode):
        return data.encode('utf-8')
    else:
        return data
