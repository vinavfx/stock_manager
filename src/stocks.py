# -----------------------------------------------------------
# AUTHOR --------> Francisco Contreras
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
import os
import re
import sys
import json
from ..python_util.util import fread
from ..env import INDEXING_DIR

stocks_data = {}


def load_data():
    global stocks_data
    stocks_data = json.loads(fread(os.path.join(INDEXING_DIR, 'stocks.json')))

    if sys.version_info[0] < 3:
        stocks_data = convert_to_utf8(stocks_data)


def get_stocks():
    return stocks_data


def convert_to_utf8(data):
    if isinstance(data, dict):
        return {convert_to_utf8(key): convert_to_utf8(value) for key, value in data.iteritems()}

    elif isinstance(data, list):
        return [convert_to_utf8(element) for element in data]

    elif isinstance(data, unicode):
        return clean_non_ascii(data).encode('utf-8')

    elif isinstance(data, str):
        return clean_non_ascii(data)

    else:
        return data


def clean_non_ascii(s):
    return re.sub(r'[^\x00-\x7F]', '', s)
