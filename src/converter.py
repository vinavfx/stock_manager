# Author: Francisco Jose Contreras Cuevas
# Office: VFX Artist - Senior Compositor
# Website: vinavfx.com
import os
import subprocess
import nuke

from ..nuke_util.media_util import get_name_no_extension, get_extension, is_sequence, get_sequence
from ..python_util.util import sh
#  from ..pipeline.deadline_submit import execute_function


def get_correct_sequence(sequence):
    basename = get_name_no_extension(sequence)

    new_sequence = '{}/{}%{}d.{}'.format(
        os.path.dirname(sequence),
        basename.replace('#', ''),
        basename.count('#'),
        get_extension(sequence)
    )

    return new_sequence

def convert(src_hash, dst, first_frame, last_frame, is_sequence, is_texture):

    ffmpeg = '/usr/bin/ffmpeg'
    src = src_hash

    basename = get_name_no_extension(src)
    name = basename.replace(' ', '_')

    if is_sequence and not is_texture:
        src = get_correct_sequence(src)
        name = name.replace('#', '')[:-1]

    output_dir = '{}/{}_{}'.format(dst,
                                   os.path.basename(os.path.dirname(src)), name)

    if os.path.isdir(output_dir):
        return name, output_dir

    os.mkdir(output_dir)

    output = '{}/{}_%d.jpg'.format(output_dir, name)

    total_frames = last_frame - first_frame
    frames = 360 if total_frames > 360 else total_frames
    scale = 400

    if is_texture:
        cmd = '{} -i "{}" -vf scale={}:-1 -q:v 1 "{}/{}.jpg"'.format(
            ffmpeg, src, scale, output_dir, basename)

    elif is_sequence:
        cmd = '{} -start_number {} -i "{}" -vf scale={}:-1 -q:v 1 -vframes {} "{}"'.format(
            ffmpeg, first_frame, src, scale, frames, output)

    else:
        seconds = frames / 24
        cmd = '{} -i "{}" -vf scale={}:-1 -q:v 1 -ss 0 -t {} "{}"'.format(
            ffmpeg, src, scale, seconds, output)

    _, stdout = sh(cmd)
    ffmpeg_error = 'Error' in stdout.decode()

    if ffmpeg_error:
        convert_data = {
            'src': src_hash,
            'output': output,
            'first_frame': first_frame,
            'last_frame': last_frame,
            'scale': scale,
            'frames': frames
        }

        #  execute_function(
            #  'vina.stock_manager.converter.convert_with_nuke', convert_data)

    return name, output_dir


def convert_with_nuke(data):
    src = data['src']
    output = data['output']
    first_frame = data['first_frame']
    last_frame = data['last_frame']
    scale = data['scale']
    frames = data['frames']

    read = nuke.createNode('Read')
    read.knob('file').fromUserText(src)
    read.knob('first').setValue(first_frame)
    read.knob('last').setValue(last_frame)

    reformat = nuke.createNode('Reformat')
    reformat.knob('type').setValue('to box')
    reformat.knob('box_width').setValue(scale)
    reformat.setInput(0, read)

    write = nuke.createNode('Write')
    write.setInput(0, reformat)
    write.knob('file').setValue(output)
    write.knob('file_type').setValue('jpeg')

    nuke.execute(write, first_frame, first_frame + frames)


def get_frames(video):

    cmd = ['ffprobe', '-show_entries', 'stream=nb_frames', '-i', video]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    out, _ = process.communicate()
    out = out.decode().split('nb_frames=')[1].split()[0]

    return int(out)


def get_format(video, start_frame):
    is_seq = is_sequence(video)

    if is_seq:
        video = get_correct_sequence(video)

    start_number = '-start_number {}'.format(start_frame) if is_seq else ''

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
        image_magick = '/usr/bin/identify'
        one_frame = get_sequence(video)[0]
        cmd = '{} -format "%wx%h" "{}"'.format(image_magick, one_frame)
        out, _ = sh(cmd)

        try:
            width = int(out.split('x')[0])
            height = int(out.split('x')[1])
        except:
            pass

    if not width or not height:
        print('Error: Format cannot be 0 !', cmd)

    return width, height

