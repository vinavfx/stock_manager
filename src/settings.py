# Author: Francisco Jose Contreras Cuevas
# Office: VFX Artist - Senior Compositor
# Website: vinavfx.com
import os
from ..python_util.util import jwrite, jread
from ..nuke_util.nuke_util import get_nuke_path

settings_file = '{}/stock_manager.json'.format(get_nuke_path())
settings = {}
loaded = False


def load_settings():
    global settings, loaded

    if loaded:
        return

    if not os.path.isfile(settings_file):
        jwrite(settings_file, {})

    settings = jread(settings_file)
    loaded = True


def save_settings():
    jwrite(settings_file, settings)


def set_setting(key, value):
    settings[key] = value
    save_settings()


def get_setting(key):
    load_settings()
    return settings.get(key)
