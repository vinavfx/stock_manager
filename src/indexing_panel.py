# Author: Francisco Jose Contreras Cuevas
# Office: VFX Artist - Senior Compositor
# Website: vinavfx.com
import os
import nuke
import threading

from . import indexing
from .converter import get_ffmpeg
from .settings import set_setting, get_stock_folder

from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTreeWidget, QTreeWidgetItem, QAbstractItemView)


class dirs_stock(QWidget):
    def __init__(self, stocks, status_bar):
        QWidget.__init__(self)

        self.stocks = stocks
        self.status_bar = status_bar
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setColumnWidth(0, 150)
        self.tree.setColumnWidth(1, 70)
        self.tree.setColumnWidth(2, 150)

        self.tree.setHeaderLabels(['Name', 'Amount', 'Path', 'Status'])
        self.tree.setAlternatingRowColors(True)
        self.tree.setAcceptDrops(True)
        self.tree.setSelectionMode(QAbstractItemView.MultiSelection)
        self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection)

        buttons_layout = QHBoxLayout()
        buttons_layout.setMargin(0)
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)

        self.set_folder_btn = QPushButton('Set Folder')
        self.set_folder_btn.clicked.connect(self.set_folder_dialog)

        self.current_folder_label = QLabel()

        self.refresh_index_btn = QPushButton('Refresh Indexs')
        self.refresh_index_btn.clicked.connect(self.refresh_indexs)

        buttons_layout.addWidget(self.refresh_index_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.current_folder_label)
        buttons_layout.addWidget(self.set_folder_btn)

        layout.addWidget(self.tree)
        layout.addWidget(buttons_widget)

        self.set_folder(get_stock_folder(), update_tree=False)

        for folder, data in indexing.get_indexed_folder().items():
            self.add_path(folder, data['indexed'], data['amount'])

        self.update_total_stocks()

    def set_folder_dialog(self):
        stock_folder = nuke.getFilename('Set Stock Path')
        if not stock_folder:
            return

        if stock_folder[-1] == '/':
            stock_folder = os.path.dirname(stock_folder)

        self.set_folder(stock_folder)


    def set_folder(self, stock_folder, update_tree=True):
        exist_folder = os.path.isdir(stock_folder)

        self.current_folder_label.setText(
            '<font color="{}">{}</font>'.format('lime' if exist_folder else 'red', stock_folder))

        if not exist_folder:
            self.refresh_index_btn.setDisabled(True)
            return

        self.refresh_index_btn.setDisabled(False)

        set_setting('stock_folder', stock_folder)
        indexing.set_stock_folder()
        indexing.load_data()

        if not update_tree:
            return

        self.tree.clear()
        indexing.clear_indexed_folder()

        for d in os.listdir(stock_folder):
            if d == 'indexing':
                continue

            path = os.path.join(stock_folder, d)

            if not os.path.isdir(path):
                continue

            self.add_path(path)


    def refresh_indexs(self):
        ffmpeg, ffprobe = get_ffmpeg()
        if not ffmpeg or not ffprobe:
            nuke.message('You need to install <b>ffmpeg</b> and <b>ffprobe</b> to index !')
            return

        self.refresh_index_btn.setText('Stop')
        self.refresh_index_btn.clicked.disconnect()

        nuke.executeInMainThread(
            self.status_bar.set_indexing_stock, ('analyzing'))

        def _stop_threads():
            self.stop_threads = True
            self.refresh_index_btn.setText('Stopping...')
            self.refresh_index_btn.setEnabled(False)

        self.refresh_index_btn.clicked.connect(_stop_threads)

        self.stop_threads = False
        threading.Thread(
            target=self.refresh_indexs_thread,
            args=(0, lambda: self.stop_threads)
        ).start()

    def refresh_indexs_thread(self, _, stop_threads):
        self.set_folder_btn.setEnabled(False)

        indexing.to_index(self.finished_index,
                          self.each_folder_index, self.each_index, stop_threads)

    def each_index(self, f, folder, percent, indexed_stocks):
        item = self.get_item(folder)
        if not item:
            return

        nuke.executeInMainThread(
            self.status_bar.set_indexing_stock, (f, percent))

        self.update_item(item, -1, indexed_stocks)
        self.update_total_stocks()

    def each_folder_index(self, folder, amount):
        item = self.get_item(folder)
        if not item:
            return

        self.update_item(item, 1, amount)

    def finished_index(self):
        self.set_folder_btn.setEnabled(True)
        self.refresh_index_btn.setText('Refresh Indexs')
        self.refresh_index_btn.clicked.disconnect()
        self.refresh_index_btn.clicked.connect(self.refresh_indexs)
        self.refresh_index_btn.setEnabled(True)

        nuke.executeInMainThread(
            self.status_bar.set_indexing_stock, ('finished'))

        self.update_total_stocks()
        nuke.executeInMainThread(self.stocks.clear_and_refresh)

    def update_item(self, item, status, amount):
        item.setText(1, str(amount))
        label = self.tree.itemWidget(item, 3)

        if not label:
            label = QLabel()
            self.tree.setItemWidget(item, 3, label)

        if status == -1:
            label.setStyleSheet('QLabel {color: rgb(255, 255, 0);}')
            label.setText('Indexing...')
        elif status == -2:
            label.setText('Disconnected')
            label.setStyleSheet('QLabel {color: rgb(255, 0, 0);}')
        elif status == 1:
            label.setStyleSheet('QLabel {color: rgb(100, 255, 0);}')
            label.setText('Indexed')
        else:
            label.setStyleSheet('QLabel {color: rgb(255, 0, 0);}')
            label.setText('Not Indexed')

    def update_total_stocks(self):
        total_stocks = indexing.get_total_stocks()

        nuke.executeInMainThread(
            self.status_bar.set_total_stocks, (total_stocks))

    def add_path(self, path, indexed=False, amount=0):
        item = QTreeWidgetItem()
        basename = os.path.basename(path)

        item.setText(0, basename)
        item.setText(1, str(amount))
        item.setText(2, basename)

        for i in [0, 1, 2]:
            item.setToolTip(
                i, 'The folder containing the name <b>"texture"</b>\nwill ignore all sequences in folder !')

        self.tree.addTopLevelItem(item)
        self.update_item(item, indexed, amount)

        if not indexed:
            indexing.save_indexed_folder(basename)

    def get_item(self, path):
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if path == item.text(2):
                return item

        return None

