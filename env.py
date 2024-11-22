import os

INDEXING_DIR = '/home/pancho/Desktop/indexing'

ROOT_STOCKS_DIRS = [
    '/home/pancho/Desktop/stocks'
]

STOCKS_DIRS = [os.path.join(root, d) for root in ROOT_STOCKS_DIRS if os.path.exists(
    root) for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]

INDEXED_DIR = os.path.join(INDEXING_DIR, 'indexed')
THUMBNAILS_DIR = os.path.join(INDEXING_DIR, 'thumbnails')
