from . import src as stock_manager
from .nuke_util import panels

panels.init(stock_manager.stock_manager.stock_manager_widget, 'Stock Manager')
