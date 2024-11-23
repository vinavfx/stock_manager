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

    if sys.version_info[0] > 2:
        return

    data = {}
    for key, value in stocks_data.items():
        non_ascii = bool(re.search(r'[^\x00-\x7F]', key))

        if non_ascii:
            continue

        data[key] = value

    stocks_data = data


def get_stocks():
    return stocks_data
