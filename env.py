import os

INDEXING_DIR = '<path_to_indexing_folder'

ROOT_STOCKS_DIRS = [
    '<path_to_stocks_folder>'
]

FFMPEG = '/usr/bin/ffmpeg'
FFPROBE = '/usr/bin/ffprobe'

STOCKS_DIRS = [os.path.join(root, d) for root in ROOT_STOCKS_DIRS if os.path.exists(
    root) for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]

STOCKS_DIRS = [
    p for p in STOCKS_DIRS if not os.path.basename(INDEXING_DIR).lower() in os.path.basename(p).lower()]

INDEXED_DIR = os.path.join(INDEXING_DIR, 'indexed')
THUMBNAILS_DIR = os.path.join(INDEXING_DIR, 'thumbnails')
METADATA_DIR = os.path.join(INDEXING_DIR, 'metadata')
