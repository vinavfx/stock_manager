# -----------------------------------------------------------
# AUTHOR --------> Francisco Contreras
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
from concurrent.futures import ProcessPoolExecutor


STOCKS_DIRS = [
    '/home/pancho/Desktop/stocks'
]

INDEXING_DIR = '/home/pancho/Desktop/indexing'
WORKERS = 4


def render_stock(stock_path):
    return


def extract_stocks():
    stocks = []

    return stocks


with ProcessPoolExecutor(max_workers=WORKERS) as executor:
    executor.map(render_stock, extract_stocks())
