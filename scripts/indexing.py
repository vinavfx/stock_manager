# -----------------------------------------------------------
# AUTHOR --------> Francisco Contreras
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
import os
import sys
import re
import subprocess
from concurrent.futures import ProcessPoolExecutor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from env import INDEXING_DIR, STOCKS_DIRS


WORKERS = 8


if not os.path.isdir(INDEXING_DIR):
    os.mkdir(INDEXING_DIR)


def render_stock(stock_path):
    return

    output = os.path.join(INDEXING_DIR, os.path.basename(stock_path))

    cmd = 'ffmpeg -i "{}" "{}"'.format(stock_path, output)

    try:
        subprocess.run(cmd, check=True, shell=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    except subprocess.CalledProcessError as e:
        print(e.stderr.decode())
        print('\n' + cmd)


def extract_stocks():
    stocks = []
    scanned_dirs = []

    for folder in STOCKS_DIRS:
        for root, _, files in os.walk(folder):
            for f in files:
                ext = f.split('.')[-1]

                if ext in ['mov', 'mp4']:
                    stock_path = os.path.join(root, f)
                    if not stock_path in stocks:
                        stocks.append(stock_path)
                    continue

                if not ext in ['jpg', 'jpeg', 'tiff', 'tif', 'png', 'exr']:
                    continue

                sequence_dir = root
                if sequence_dir in scanned_dirs:
                    continue
                scanned_dirs.append(sequence_dir)

                sequences, textures = separate_images_and_sequences(
                    sequence_dir)

                stocks.extend(sequences)
                stocks.extend(textures)

    return stocks


def separate_images_and_sequences(folder):
    files = sorted(os.listdir(folder))
    sequence_pattern = re.compile(r"(.*?)(\d+)(\.\w+)$")

    unique_images = []
    sequences = {}

    for file in files:
        match = sequence_pattern.match(file)
        if match:
            base, _, ext = match.groups()
            sequences[f"{base}{ext}"] = f"{folder}/{base}%04d{ext}"
        else:
            unique_images.append(os.path.join(folder, file))

    return list(sequences.values()), unique_images


with ProcessPoolExecutor(max_workers=WORKERS) as executor:
    executor.map(render_stock, extract_stocks())
