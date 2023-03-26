import nuke
from sys import version_info

if version_info.major == 3:
    from . import src as stock_manager
    from .nuke_util import panels


def setup():
    if not version_info.major == 3:
        nuke.message(
            '"Stock Manager" only works on a higher version of nuke with Python 3 !')
        return

    panels.init('stock_manager.stock_manager.stock_manager.stock_manager_widget',
                'Stock Manager')
