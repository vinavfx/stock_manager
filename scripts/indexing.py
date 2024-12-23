# -----------------------------------------------------------
# AUTHOR --------> Francisco Contreras
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
import os
import shutil
import sys
import traceback
import re
import subprocess
from tqdm import tqdm
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor



sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env import *
from python_util.util import jwrite, sh, jread


THREAD = 32
min_sequence_length = 24
ignore_patterns = ['preview', 'Preview', 'proxy', 'Proxy', 'EXR']
force_texture_patterns = ['texture']
min_video_pixels = 720 * 480
min_image_pixels = 320 * 240

videos_allowed = ['mov', 'mp4']
images_allowed = ['jpg', 'jpeg', 'tiff', 'tif', 'png', 'exr']

if not os.path.isdir(INDEXED_DIR):
    os.makedirs(INDEXED_DIR)

if not os.path.isdir(THUMBNAILS_DIR):
    os.makedirs(THUMBNAILS_DIR)

if not os.path.isdir(METADATA_DIR):
    os.makedirs(METADATA_DIR)


def render_stock(_stock):
    stock, folder = _stock
    is_sequence = not type(stock) == str
    stock_path = stock[0] if is_sequence else stock
    padding = stock[1][0][2] if is_sequence else ''
    ext = stock_path.split('.')[-1].lower()

    if ext not in videos_allowed and ext not in images_allowed:
        return

    name = basename = os.path.basename(stock_path).rsplit('.', 1)[0]
    basename = name.rsplit(padding, 1)[0][:-1] if is_sequence else name

    new_name = '{}_{}'.format(
        os.path.basename(os.path.dirname(stock_path)), basename)

    output_dir = '{}/{}'.format(INDEXED_DIR, new_name)
    if os.path.isdir(output_dir):
        return

    first_frame = 1
    total_frames = 1
    frame_rate = 24

    if ext in videos_allowed:
        total_frames, frame_rate = get_frames(stock_path)
    elif is_sequence:
        first_frame = int(stock[1][0][1])
        total_frames = len(stock[1])

    if not total_frames:
        return

    resolution = get_format(stock_path, first_frame, is_sequence)
    pixels = resolution[0] * resolution[1]

    if not pixels:
        return

    min_pixels = min_image_pixels if total_frames == 1 else min_video_pixels
    if pixels < min_pixels:
        return

    if os.path.isdir(output_dir):
        return

    os.mkdir(output_dir)

    frames = 300 if total_frames > 300 else total_frames
    scale = 400

    output = '{}/{}_%d.jpg'.format(output_dir, basename)

    if ext in videos_allowed:
        seconds = float(frames) / float(frame_rate)

        cmd = '{} -i "{}" -vf scale={}:-1 -q:v 1 -ss 0 -t {} "{}"'.format(
            FFMPEG, stock_path, scale, seconds, output)

    elif is_sequence:
        cmd = '{} -start_number {} -i "{}" -vf scale={}:-1 -q:v 1 -vframes {} "{}"'.format(
            FFMPEG, first_frame, stock_path, scale, frames, output)

    else:
        cmd = '{} -i "{}" -vf scale={}:-1 -q:v 1 "{}/{}.jpg"'.format(
            FFMPEG, stock_path, scale, output_dir, basename)

    try:
        subprocess.run(cmd, check=True, shell=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    except subprocess.CalledProcessError as _:
        print('\nError Here:')
        print(cmd)

    create_thumbnail(output_dir)

    metadata = {
        'frames': total_frames,
        'indexed': new_name,
        'resolution': resolution,
        'tag': get_tag(stock_path),
        'folder': os.path.basename(folder),
        'first_frame': first_frame,
        'last_frame': first_frame + total_frames - 1,
        'name': basename,
        'path': stock_path
    }

    jwrite('{}/{}.json'.format(METADATA_DIR, new_name), metadata)


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

    if not parent_name and not grandparent_name:
        name = 'no_tag'

    elif not parent_name:
        name = ' '.join(grandparent_name)

    elif (not grandparent_name) or (parent_name == grandparent_name) or (grandparent_name == root_stock):
        name = ' '.join(parent_name)

    else:
        first_name = ' '.join(grandparent_name)
        last_name = ' '.join(parent_name)
        name = '{} - {}'.format(first_name, last_name)

    return name


def get_frames(video):
    cmd = [FFPROBE, '-show_entries',
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

        frame_rate = 0
        frames = 0

    return frames, frame_rate


def get_format(video, start_frame, is_sequence):

    start_number = '-start_number {}'.format(
        start_frame) if is_sequence else ''

    cmd = '{} {} -show_entries stream=width,height -i "{}"'.format(
        FFPROBE, start_number, video)

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

    cmd = '{} -i "{}" -vf scale=120:-1 -q:v 1 "{}"'.format(FFMPEG, src, thumbnail)
    subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE)


def extract_stocks():
    scanning_file = os.path.join(INDEXING_DIR, 'scanning.json')

    try:
        stocks = jread(scanning_file)
        return stocks
    except:
        pass

    print('Scanning Stocks ...')

    stocks = []
    scanned_dirs = []
    unique_files = {}

    for folder in STOCKS_DIRS:
        for root, _, files in os.walk(folder):
            for f in files:
                if any(p in f for p in ignore_patterns):
                    continue

                if any(p in root for p in ignore_patterns):
                    continue

                stock_path = os.path.join(root, f)

                key = (f, os.path.getsize(stock_path))
                if key in unique_files:
                    continue

                unique_files[key] = None

                ext = f.split('.')[-1].lower()

                if ext in videos_allowed:
                    stocks.append((stock_path, folder))
                    continue

                if not ext in images_allowed:
                    continue

                if any(t in root.lower() for t in force_texture_patterns):
                    stocks.append((stock_path, folder))
                    continue

                sequence_dir = root
                if sequence_dir in scanned_dirs:
                    continue
                scanned_dirs.append(sequence_dir)

                sequences, textures = separate_images_and_sequences(
                    sequence_dir)

                stocks.extend([(seq, folder) for seq in sequences])
                stocks.extend([(tex, folder) for tex in textures])

    jwrite(scanning_file, stocks)
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
            padding = '%0{}d'.format(len(frame))
            key = '{}/{}{}{}'.format(folder, base, padding, ext)
            potential_sequences[key].append((file, frame, padding))
        else:
            unique_images.append(os.path.join(folder, file))

    valid_sequences = []
    for key, frames in potential_sequences.items():
        if len(frames) > min_sequence_length:
            valid_sequences.append((key, frames))
        else:
            for frame in frames:
                unique_images.append(os.path.join(folder, frame[0]))

    return valid_sequences, unique_images


def delete_disconnected_stocks():
    textures_data = jread(os.path.join(INDEXING_DIR, 'textures.json'))
    stocks_data = jread(os.path.join(INDEXING_DIR, 'stocks.json'))
    stocks_data.update(textures_data)

    deleted = 0
    for stock_path, data in stocks_data.items():
        if os.path.isfile(stock_path):
            continue

        basename = os.path.basename(stock_path)
        if any(i in basename for i in ['%', 'd']):
            if os.path.isdir(os.path.dirname(stock_path)):
                continue

        delete_indexed_stock(data['indexed'])
        deleted += 1

    create_stocks_json()
    print('{} Stocks Deleted.'.format(deleted))


def delete_indexed_stock(name):
    basename = os.path.basename(name).rsplit('.', 1)[0]

    indexed_path = os.path.join(INDEXED_DIR, basename)
    thumbnail_path = '{}/{}.jpg'.format(THUMBNAILS_DIR, basename)
    metadata_path = '{}/{}.json'.format(METADATA_DIR, basename)

    if os.path.isfile(metadata_path):
        os.remove(metadata_path)

    if os.path.isdir(indexed_path):
        shutil.rmtree(indexed_path)

    if os.path.isfile(thumbnail_path):
        os.remove(thumbnail_path)


def delete_corrupt_indexed_stock(name):
    basename = os.path.basename(name).rsplit('.', 1)[0]

    indexed_path = os.path.join(INDEXED_DIR, basename)
    thumbnail_path = '{}/{}.jpg'.format(THUMBNAILS_DIR, basename)
    metadata_path = '{}/{}.json'.format(METADATA_DIR, basename)

    if (os.path.isfile(metadata_path)
        and os.path.isdir(indexed_path)
            and os.path.isfile(thumbnail_path)):
        return

    delete_indexed_stock(name)


def create_stocks_json():
    stocks = {}
    textures = {}

    for f in os.listdir(METADATA_DIR):
        metadata_path = os.path.join(METADATA_DIR, f)

        try:
            data = jread(metadata_path)
        except:
            continue

        path = data['path']
        del data['path']

        if data['frames'] == 1:
            textures[path] = data
        else:
            stocks[path] = data

    stocks = dict(sorted(stocks.items(), key=lambda i: i[1]['name'].lower()))
    textures = dict(sorted(textures.items(), key=lambda i: i[1]['name'].lower()))

    jwrite(os.path.join(INDEXING_DIR, 'stocks.json'), stocks)
    jwrite(os.path.join(INDEXING_DIR, 'textures.json'), textures)


def delete_corrupt_stocks():
    corrupt_metadata = []

    for f in os.listdir(METADATA_DIR):
        metadata_path = os.path.join(METADATA_DIR, f)

        try:
            jread(metadata_path)
        except:
            corrupt_metadata.append(metadata_path)

    [delete_indexed_stock(f) for f in corrupt_metadata]
    [delete_corrupt_indexed_stock(f) for f in os.listdir(INDEXED_DIR)]
    [delete_corrupt_indexed_stock(f) for f in os.listdir(THUMBNAILS_DIR)]
    [delete_corrupt_indexed_stock(f) for f in os.listdir(METADATA_DIR)]


def render_wrapper(stock_path):
    try:
        render_stock(stock_path)
    except:
        print(traceback.format_exc())

    return stock_path


stocks = extract_stocks()

try:
    with ProcessPoolExecutor(max_workers=THREAD) as executor:
        with tqdm(total=len(stocks), desc='Indexing Stocks', unit=' Stock') as progress_bar:
            for _ in executor.map(render_wrapper, stocks):
                progress_bar.update(1)
except:
    pass


delete_corrupt_stocks()
create_stocks_json()
