# -----------------------------------------------------------
# AUTHOR --------> Francisco Contreras
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
import os
import re
import sys
from collections import OrderedDict
from ..python_util.util import jread
from ..env import INDEXING_DIR

stocks_data = {}
textures_data = {}
combined_data = {}


def load_data():
    global stocks_data, textures_data, combined_data

    stocks_data = jread(os.path.join(INDEXING_DIR, 'stocks.json'))
    textures_data = jread(os.path.join(INDEXING_DIR, 'textures.json'))

    if sys.version_info[0] == 2:
        stocks_data = non_ascii(stocks_data)
        textures_data = non_ascii(textures_data)

    combined_data = OrderedDict(stocks_data)
    combined_data.update(textures_data)


def non_ascii(data):
    new_data = OrderedDict()

    for key, value in data.items():
        non_ascii = bool(re.search(r'[^\x00-\x7F]', key))

        if non_ascii:
            continue

        new_data[key] = value

    return new_data


def get_stocks(stocks=True, textures=True):
    if stocks and textures:
        return combined_data
    elif stocks:
        return stocks_data
    elif textures:
        return textures_data
    else:
        return {}
