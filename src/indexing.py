# Author: Francisco Jose Contreras Cuevas
# Office: VFX Artist - Senior Compositor
# Website: vinavfx.com

import os
import shutil
import nuke

from ..python_util.util import jread, jwrite
from . import converter
from ..nuke_util.nuke_util import get_nuke_path
from ..nuke_util.media_util import get_extension, get_sequence

data = {}

stock_elements = [
    'atmosphere', 'blood', 'charge', 'couch', 'debris', 'lightbulb', 'cement', 'rock', 'wood', 'dust',
    'particle', 'fire', 'torch', 'glass', 'flash', 'cork', 'powder', 'smoke', 'spark', 'fireball',
    'welding', 'wall', 'shell', 'water', 'rain', 'hole', 'metal', 'concrete', 'flesh', 'windshield',
    'snow', 'embers', 'fog', 'paint', 'combust', 'ink', 'slime', 'bokeh', 'rain', 'brick', 'fabric',
    'camouflage', 'carpet', 'trims', 'leather', 'rattan', 'fruit', 'seeds', 'spices', 'vegetables', 'food',
    'crackles', 'grunge', 'paper', 'scratches', 'landscapes', 'metal', 'flower', 'plaster', 'plastic',
    'rubber', 'tape', 'styrefoam', 'skies', 'foam', 'plain', 'waterfall', 'wrinkles', 'tiles'
]

stock_types = [
    'burst', 'hit', 'splat', 'squirt', 'close', 'side', 'bouncing', 'collapse', 'fall',
    'fllying', 'shatter', 'dirt', 'cam', 'blowout', 'wave', 'explosion', 'day', 'wide',
    'turbulent', 'big', 'small', 'windy', 'smash', 'automatic', 'suppressed', 'straight', 'dark',
    'puffy', 'wisp', 'crack', 'slow', 'front', 'blast', 'burn', 'grunge', 'exploding', 'shadow',
    'beauty', 'medium', 'rising', 'mid', 'throw', 'explode', 'slomo', 'rampant', 'blot', 'chamber',
    'run', 'drip', 'rings', 'rolling', 'tendril', 'surface', 'pull', 'thin', 'tear', 'drop', 'pool',
    'large', 'flicker', 'pulsating', 'shaky', 'steady', 'dense', 'sparkles', 'fleck', 'lit', 'speck',
    'gold', 'silver', 'heavy', 'dirty', 'messy', 'persian', 'weird', 'marbled', 'bare', 'base', 'leaking',
    'galvanized', 'painted', 'clear', 'dusk', 'partial', 'sunset', 'overcast', 'cirrus', 'burned', 'ends',
    'rough', 'studded', 'cloudy', 'fuming', 'roar', 'beautiful', 'staringat', 'dying', 'stream'
]

stock_manager_folder = '{}/stock_manager_indexing'.format(get_nuke_path())

index_folder = stock_manager_folder + '/indexed'
thumbnails_folder = stock_manager_folder + '/thumbnails'
folders_data = stock_manager_folder + '/folders.json'
stocks_data = stock_manager_folder + '/stocks.json'
indexing = False

if not os.path.isdir(index_folder):
    os.makedirs(index_folder)

if not os.path.isdir(thumbnails_folder):
    os.makedirs(thumbnails_folder)


def load_data():
    global data

    if not os.path.isdir(stock_manager_folder):
        os.mkdir(stock_manager_folder)

    if os.path.isfile(folders_data):
        folders = jread(folders_data)
    else:
        folders = {}
        jwrite(folders_data, folders)

    if os.path.isfile(stocks_data):
        stocks = jread(stocks_data)
    else:
        stocks = {}
        jwrite(stocks_data, stocks)

    data = {
        'folders': folders,
        'stocks': stocks
    }


def save_data():
    global data

    new_data = {}
    new_data['folders'] = data['folders']
    new_data['stocks'] = {}

    for key, stock in data['stocks'].items():
        _stock = stock.copy()

        for k in ['item', 'mounted', 'hide']:
            if k in _stock:
                del _stock[k]

        new_data['stocks'][key] = _stock

    jwrite(stocks_data, new_data['stocks'])
    jwrite(folders_data, new_data['folders'])


def get_indexed_folder():
    return data['folders']


def get_indexed_stocks():
    return data['stocks']


def get_total_stocks():
    total_stocks = 0
    for _, data in get_indexed_folder().items():
        total_stocks += data['amount']

    return total_stocks


def is_indexing():
    return indexing


def to_index(finished_fn, each_folder_fn, each_fn, stop_threads):
    global indexing
    indexing = True

    refresh_indexs()

    total_stocks = 0

    folders = []
    for folder, folder_data in get_indexed_folder().items():
        stocks = []
        for stock in get_stocks_from_folder(folder):
            path = stock[0]
            is_sequence = stock[4]

            will_index = False

            if not path in data['stocks']:
                will_index = True
            elif not os.path.isdir(data['stocks'][path]['indexed']):
                will_index = True
            elif not os.listdir(data['stocks'][path]['indexed']):
                will_index = True

            if not is_sequence:
                if os.path.getsize(path) < 10000:
                    continue

            if will_index:
                stocks.append(stock)
            else:
                create_thumbnail(data['stocks'][path]['indexed'])

        total_stocks += len(stocks)

        folders.append([folder, folder_data, stocks])

    general_indexed_stocks = 0

    for folder, folder_data, stocks in folders:

        indexed_stocks = folder_data['amount']

        for path, first_frame, last_frame, frames, is_sequence in stocks:
            f = os.path.basename(path)

            if not is_sequence and not frames == 1:
                frames = converter.get_frames(path)
                first_frame = 1
                last_frame = frames

            general_indexed_stocks += 1
            percent = int(general_indexed_stocks * 100 / total_stocks)

            name, indexed_dir = converter.convert(
                path, index_folder, first_frame, last_frame, is_sequence, frames == 1)

            create_thumbnail(indexed_dir)

            indexed_stocks += 1
            each_fn(f, folder, percent, indexed_stocks)

            width, height = converter.get_format(path, first_frame)

            data['stocks'][path] = {
                'path': path,
                'element': '',
                'type': '',
                'folder': folder,
                'name': name,
                'resolution': [width, height],
                'indexed': indexed_dir,
                'passes': False,
                'frames': frames,
                'first_frame': first_frame,
                'last_frame': last_frame,
                'is_sequence': is_sequence
            }

            if stop_threads():
                break

        each_folder_fn(folder, indexed_stocks)
        data['folders'][folder]['indexed'] = True

        if stop_threads():
            break

    update_stocks_tag()
    calculate_amount_by_folder()

    if not stop_threads():
        garbage_remove()

    save_data()

    finished_fn()
    indexing = False


def update_stocks_tag():
    for path, stock in get_indexed_stocks().items():
        stock['element'] = detect_element(path)
        stock['type'] = detect_type(path)


def create_thumbnail(indexed_stock):
    thumbnail = '{}/{}.jpg'.format(thumbnails_folder,
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

    ffmpeg, _ = converter.get_ffmpeg()

    cmd = '{} -i "{}" -vf scale=120:-1 -q:v 1 "{}"'.format(
        ffmpeg, src, thumbnail)

    os.system(cmd)


def calculate_amount_by_folder():
    for _, indexed in get_indexed_folder().items():
        indexed['amount'] = 0

    for _, stock in get_indexed_stocks().items():
        folder = stock['folder']
        if not folder in data['folders']:
            continue

        data['folders'][folder]['amount'] += 1


def save_indexed_folder(folder):

    data['folders'][folder] = {
        'path': folder,
        'indexed': False,
        'amount': 0
    }

    save_data()


def get_stocks_from_folder(folder):

    force_textures = 'texture' in os.path.basename(folder).lower()

    stocks = []
    scanned_dirs = []

    for root, _, files in os.walk(folder):
        for name in files:
            file = os.path.join(root, name).replace('\\', '/')
            ext = get_extension(file).lower()

            if ext == 'mov' or ext == 'mp4':
                stock = [file, None, None, None,  False]
                if not stock in stocks:
                    stocks.append(stock)

            elif ext in ['jpg', 'jpeg', 'tiff', 'tif', 'png', 'exr']:
                sequence_dir = os.path.dirname(file)
                if sequence_dir in scanned_dirs:
                    continue

                scanned_dirs.append(sequence_dir)

                if force_textures:
                    for l in os.listdir(sequence_dir):
                        texture = os.path.join(sequence_dir, l)
                        stock = [texture, 1, 1, 1, False]
                        if not stock in stocks:
                            stocks.append(stock)

                    continue

                textures, sequences = separate_texture_and_sequence(
                    sequence_dir)

                for texture in textures:
                    stock = [texture, 1, 1, 1, False]
                    if not stock in stocks:
                        stocks.append(stock)

                for stock in sequences:
                    if not stock in stocks:
                        stocks.append(stock)

    return stocks


def separate_texture_and_sequence(folder):
    textures = []
    sequences = []

    sequences_to_textures = []

    min_frames = 24

    for sequence in nuke.getFileNameList(folder, True):
        try:
            seq_name, frange = sequence.rsplit(' ', 1)
        except:
            textures.append(os.path.join(folder, sequence).replace('\\', '/'))
            continue

        if not get_extension(seq_name):
            continue

        first, last = frange.split('-')
        first_frame = int(first)
        last_frame = int(last)
        frames = last_frame - first_frame + 1

        if frames < min_frames:
            sequences_to_textures.append((seq_name, first_frame, last_frame))
            continue

        sequence = [os.path.join(folder, seq_name).replace('\\', '/'),
                    first_frame, last_frame, frames, True]

        sequences.append(sequence)

    for filename, first, last in sequences_to_textures:
        sequence = os.path.join(folder, filename)
        for texture in get_sequence(sequence, [first, last]):
            textures.append(texture)

    return textures, sequences


def match_to_tags(name, tags):
    matches = []

    for tag in tags:
        if tag in name.lower():
            matches.append(tag)

    if not matches:
        return 'not labeled'

    return max(matches, key=len)


def detect_type(stock_file):
    stock_name = os.path.basename(stock_file)
    return match_to_tags(stock_name, stock_types)


def detect_element(stock_file):
    _type = match_to_tags(os.path.basename(stock_file), stock_elements)
    if not _type == 'not labeled':
        return _type

    return match_to_tags(os.path.basename(os.path.dirname(stock_file)), stock_elements)


def remove_stock(indexed_dir):
    if not os.path.isdir(indexed_dir):
        return

    shutil.rmtree(indexed_dir)
    thumbnail = '{}/{}.jpg'.format(thumbnails_folder,
                                   os.path.basename(indexed_dir))
    if os.path.isfile(thumbnail):
        os.remove(thumbnail)


def refresh_indexs():
    folders = data['folders']

    to_delete = []
    for _, stock in data['stocks'].items():
        folder = stock['folder']

        if folder in folders and not os.path.isdir(folder):
            continue

        path = stock['path']

        if stock['is_sequence']:
            if not os.path.isdir(os.path.dirname(path)):
                to_delete.append(stock)

        elif not os.path.isfile(path):
            to_delete.append(stock)

        if not folder in folders:
            if not stock in to_delete:
                to_delete.append(stock)

    for stock in to_delete:
        key = stock['path']
        del data['stocks'][key]

        indexed_dir = stock['indexed']
        remove_stock(indexed_dir)


def garbage_remove():

    indexed_folders = []
    for _, stock in data['stocks'].items():
        indexed_folders.append(stock['indexed'])

    for name in os.listdir(index_folder):
        folder = os.path.join(index_folder, name).replace('\\', '/')
        if folder in indexed_folders:
            continue

        remove_stock(folder)


def delete_folder(folder):
    del data['folders'][folder]
    save_data()
