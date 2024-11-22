# -----------------------------------------------------------
# AUTHOR --------> Francisco Contreras
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
import os
import sys
import re
import subprocess
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env import INDEXING_DIR, STOCKS_DIRS, INDEXED_DIR, THUMBNAILS_DIR, ROOT_STOCKS_DIRS
from python_util.util import jwrite, sh


WORKERS = 8
min_sequence_length = 24


if not os.path.isdir(INDEXED_DIR):
    os.makedirs(INDEXED_DIR)

if not os.path.isdir(THUMBNAILS_DIR):
    os.makedirs(THUMBNAILS_DIR)


def render_stock(stock, stocks_metadata):
    stock_path, folder = stock

    basename = os.path.basename(stock_path).rsplit('_', 1)[0].rsplit('.', 1)[0]
    indexed_relative = '{}_{}'.format(
        os.path.basename(os.path.dirname(stock_path)), basename)

    output_dir = '{}/{}'.format(INDEXED_DIR, indexed_relative)

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    if os.listdir(output_dir):
        return

    total_frames, frame_rate = get_frames(stock_path)
    first_frame = 1

    frames = 300 if total_frames > 300 else total_frames
    scale = 400

    output = '{}/{}_%d.jpg'.format(output_dir, basename)

    ext = stock_path.split('.')[-1].lower()
    is_sequence = False

    if ext in ['mp4', 'mov']:
        seconds = float(frames) / float(frame_rate)

        cmd = 'ffmpeg -i "{}" -vf scale={}:-1 -q:v 1 -ss 0 -t {} "{}"'.format(
            stock_path, scale, seconds, output)

    elif any(fmt in stock_path for fmt in ['%02d', '%03d', '%04d', '%05d']):
        is_sequence = True
        cmd = 'ffmpeg -start_number {} -i "{}" -vf scale={}:-1 -q:v 1 -vframes {} "{}"'.format(
            first_frame, stock_path, scale, frames, output)

    else:
        cmd = 'ffmpeg -i "{}" -vf scale={}:-1 -q:v 1 "{}/{}.jpg"'.format(
            stock_path, scale, output_dir, basename)

    try:
        subprocess.run(cmd, check=True, shell=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    except subprocess.CalledProcessError as _:
        print('\nError Here:')
        print(cmd)

    create_thumbnail(output_dir)

    stocks_metadata[stock_path] = {
        'frames': total_frames,
        'indexed': indexed_relative,
        'resolution': get_format(stock_path, first_frame, is_sequence),
        'tag': get_tag(stock_path),
        'folder': os.path.basename(folder),
        'first_frame': first_frame,
        'last_frame': first_frame + total_frames - 1,
        'name': basename
    }


def get_tag(stock_file):
    stock_file = get_relative_stock_path(stock_file)

    def word_separator(text):
        min_word_size = 2

        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', text)
        words = [w.lower() for w in words if len(w) > min_word_size]
        return words

    root_stock = word_separator(stock_file.split('/')[0])

    parent = os.path.dirname(stock_file)
    grandparent = os.path.dirname(parent)

    parent_name = word_separator(os.path.basename(parent))
    grandparent_name = word_separator(os.path.basename(grandparent))

    if (not grandparent_name) or (parent_name == grandparent_name) or (grandparent_name == root_stock):
        name = ' '.join(parent_name)
    else:
        first_name = ' '.join(grandparent_name)
        last_name = ' '.join(parent_name)
        name = '{} - {}'.format(first_name, last_name)

    return name


def get_frames(video):
    cmd = ['ffprobe', '-show_entries',
           'stream=nb_frames,avg_frame_rate', '-i', video]
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        out, _ = process.communicate()
        nb_frames = out.decode().split('nb_frames=')[1].split()[0]
        avg_frame_rate = out.decode().split('avg_frame_rate=')[1].split()[0]

        fr1, fr2 = avg_frame_rate.split('/')
        frame_rate = float(fr1) / float(fr2)
        frames = int(nb_frames)

    except:

        frame_rate = 24.0
        frames = 1

    return frames, frame_rate


def get_format(video, start_frame, is_sequence):

    start_number = '-start_number {}'.format(
        start_frame) if is_sequence else ''

    cmd = 'ffprobe {} -show_entries stream=width,height -i "{}"'.format(
        start_number, video)

    out, _ = sh(cmd)

    width = 0
    height = 0

    try:
        width = int(out.split('width=')[1].split()[0])
        height = int(out.split('height=')[1].split()[0])
    except:
        pass

    if not width or not height:
        print('Error: Format cannot be 0 !', cmd)

    return width, height


def create_thumbnail(indexed_stock):
    thumbnail = '{}/{}.jpg'.format(THUMBNAILS_DIR,
                                   os.path.basename(indexed_stock))

    if os.path.isfile(thumbnail):
        return

    ref_size = 0
    src = ''
    for f in os.listdir(indexed_stock):
        pic = os.path.join(indexed_stock, f)

        size = os.path.getsize(pic)
        if size >= ref_size:
            ref_size = size
            src = pic

    cmd = 'ffmpeg -i "{}" -vf scale=120:-1 -q:v 1 "{}"'.format(src, thumbnail)
    subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE)


def extract_stocks():
    stocks = []
    scanned_dirs = []

    for folder in STOCKS_DIRS:
        for root, _, files in os.walk(folder):
            for f in files:
                ext = f.split('.')[-1].lower()

                if ext in ['mov', 'mp4']:
                    stock_path = os.path.join(root, f)
                    if not stock_path in stocks:
                        stocks.append((stock_path, folder))
                    continue

                if not ext in ['jpg', 'jpeg', 'tiff', 'tif', 'png', 'exr']:
                    continue

                sequence_dir = root
                if sequence_dir in scanned_dirs:
                    continue
                scanned_dirs.append(sequence_dir)

                sequences, textures = separate_images_and_sequences(
                    sequence_dir)

                stocks.extend([(seq, folder) for seq in sequences])
                stocks.extend([(tex, folder) for tex in textures])

    return stocks


def get_relative_stock_path(path):
    relative_path = next((os.path.relpath(path, root)
                         for root in ROOT_STOCKS_DIRS if path.startswith(root)), None)

    if relative_path:
        return relative_path

    return path


def separate_images_and_sequences(folder):
    files = sorted(os.listdir(folder))
    sequence_pattern = re.compile(r"(.*?)(\d+)(\.\w+)$")

    unique_images = []
    potential_sequences = defaultdict(list)

    for file in files:
        match = sequence_pattern.match(file)
        if match:
            base, frame, ext = match.groups()
            potential_sequences[f"{base}{ext}"].append(file)
        else:
            unique_images.append(os.path.join(folder, file))

    valid_sequences = []
    for _, frames in potential_sequences.items():
        if len(frames) > min_sequence_length:
            match = sequence_pattern.match(frames[0])
            if match:
                base, frame, ext = match.groups()
                frame_length = len(frame)
                sequence_path = f"{folder}/{base}%0{frame_length}d{ext}"
                valid_sequences.append(sequence_path)
        else:
            for frame in frames:
                unique_images.append(os.path.join(folder, frame))

    return valid_sequences, unique_images


with Manager() as manager:
    stocks_metadata = manager.dict()

    def render_wrapper(stock_path):
        render_stock(stock_path, stocks_metadata)

    with ProcessPoolExecutor(max_workers=WORKERS) as executor:
        executor.map(render_wrapper, extract_stocks())

    jwrite(os.path.join(INDEXING_DIR, 'stocks.json'), dict(stocks_metadata))
