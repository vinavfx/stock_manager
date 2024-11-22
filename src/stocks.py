# -----------------------------------------------------------
# AUTHOR --------> Francisco Contreras
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
import os
from ..python_util.util import jread
from ..env import INDEXING_DIR

stocks_data = {}


def load_data():
    global stocks_data
    stocks_data = jread(os.path.join(INDEXING_DIR, 'stocks.json'))


def get_stocks():
    return stocks_data
