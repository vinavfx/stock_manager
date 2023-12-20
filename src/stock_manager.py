# -----------------------------------------------------------
# AUTHOR --------> Francisco Jose Contreras Cuevas
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
import nuke

from PySide2.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QLabel)

from .indexing_panel import dirs_stock
from .player_panel import player
from .stocks_panel import stocks
from . import indexing

from ..nuke_util.panels import panel_widget


class status_bar(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        layout = QHBoxLayout()
        layout.setContentsMargins(12, 0, 12, 0)
        self.setLayout(layout)

        self.total_label = QLabel()
        self.indexing_stock = QLabel()
        self.current_stock = QLabel()
        self.visibles_label = QLabel()

        layout.addWidget(self.current_stock)
        layout.addStretch()
        layout.addWidget(self.total_label)
        layout.addWidget(self.indexing_stock)
        layout.addStretch()
        layout.addWidget(self.visibles_label)


    def set_indexing_stock(self, stock_name, percent=0):
        if stock_name == 'finished':
            self.indexing_stock.setText('')
            return

        if stock_name == 'analyzing':
            text = '<font color="#fcba03">Analyzing directories...</font>'
        else:
            text = '<font color="#fcba03">Indexing:</font> {}... <font color="#64C8FA">{}%</font>'.format(
                stock_name, percent)

        text = '( {} )'.format(text)
        self.indexing_stock.setText(text)

    def set_total_stocks(self, total):
        self.total_label.setText(
            'Total: <font color="#64C8FA">{}</font> stocks'.format(total))


    def set_current_stock(self, stock):
        width, height = stock['resolution']

        data_text = '<font color="#64C8FA"><i>{}x{}</i></font>'.format(
            width, height)

        left_text = '{} - {}'.format(stock['name'], data_text)
        right_text = '<font color="#ffbb00"><b>{}</b></font> frames'.format( stock['frames'])

        if stock['frames'] == 1:
            right_text = 'Texture'

        text = '{} - {}'.format(left_text, right_text)

        self.current_stock.setText(text)

    def set_visibles_label(self, visibles, total):

        visibles_text = '<font color="{}">{} / </font>'.format(
            '#00ff40' if visibles == total else '#c4c4c4', visibles)

        total_text = '<font color="{}">{}</font>'.format(
            '#00ff40' if visibles == total else '#ff0000', total)

        text = '{} {}'.format(visibles_text, total_text)
        self.visibles_label.setText(text)


class stock_manager_widget(panel_widget):
    def __init__(self, parent=None):
        panel_widget.__init__(self, parent)
        self.mounted = False

    def tab_changed(self):
        if self.tabs.currentIndex() == 1:
            return

        if indexing.is_indexing():
            nuke.message('Now it is indexing !')
            self.tabs.setCurrentIndex(1)

    def setup(self):
        self.mounted = True

        layout = QVBoxLayout()
        layout.setMargin(0)

        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.tab_changed)

        viewer_layout = QVBoxLayout()
        viewer_layout.setMargin(0)
        viewer = QWidget()
        viewer.setLayout(viewer_layout)
        self.tabs.addTab(viewer, 'Viewer')

        manage_layout = QVBoxLayout()
        manage_layout.setMargin(0)
        manage = QWidget()
        manage.setLayout(manage_layout)
        self.tabs.addTab(manage, 'Indexing')

        self.tabs.setCurrentIndex(0)

        _status_bar = status_bar()
        _player = player()
        _stocks = stocks(_player, _status_bar)
        _dirs_stock = dirs_stock(_stocks, _status_bar)

        manage_layout.addWidget(_dirs_stock)
        viewer_layout.addWidget(_player)
        viewer_layout.addWidget(_stocks)

        layout.addWidget(self.tabs)
        layout.addWidget(_status_bar)

        self.setLayout(layout)

    def showEvent(self, event):
        super(stock_manager_widget, self).showEvent(event)

        if not self.mounted:
            self.setup()
