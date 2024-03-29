# -----------------------------------------------------------
# AUTHOR --------> Francisco Jose Contreras Cuevas
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
import os
import nuke
import threading

from . import indexing
from .converter import get_ffmpeg
from .settings import set_setting, get_stock_folder

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMenu, QAction,
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
        self.tree.setColumnWidth(0, 350)
        self.tree.setColumnWidth(1, 70)

        self.tree.setHeaderLabels(['Name', 'Amount', 'Status'])
        self.tree.setAlternatingRowColors(True)
        self.tree.setAcceptDrops(True)
        self.tree.setSelectionMode(QAbstractItemView.MultiSelection)
        self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_menu)

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

        self.set_folder(get_stock_folder())

    def show_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)

        def rescan():
            for i in self.tree.selectedItems():
                self.update_item(i, 2)
                value = i.text(0) == 'Indexed'
                indexing.set_folder_value(i.text(0), 'indexed', value)

        rescan_action = QAction('Rescan Folder', self)
        rescan_action.triggered.connect(rescan)

        menu.addAction(rescan_action)

        menu.exec_(self.tree.mapToGlobal(pos))

    def set_folder_dialog(self):
        stock_folder = nuke.getFilename('Set Stock Path')
        if not stock_folder:
            return

        if stock_folder[-1] == '/':
            stock_folder = os.path.dirname(stock_folder)

        self.set_folder(stock_folder)

    def set_folder(self, stock_folder):
        exist_folder = os.path.isdir(stock_folder)
        self.current_folder_label.setText(
            '<font color="{}">{}</font>'.format('lime' if exist_folder else 'red', stock_folder))

        set_setting('stock_folder', stock_folder)

        self.tree.clear()
        indexing.set_stock_folder()
        indexing.load_data()

        if not os.path.isdir(stock_folder):
            return

        indexed_folder = indexing.get_indexed_folder()
        stock_folder_list = os.listdir(stock_folder)

        for folder, data in sorted(indexed_folder.items()):
            if folder in stock_folder_list:
                self.add_path(folder, data['indexed'], data['amount'])
            else:
                indexing.remove_indexed_folder(folder)

        for d in stock_folder_list:
            if d == 'indexing':
                continue

            path = os.path.join(stock_folder, d)

            if not os.path.isdir(path):
                continue

            if d in indexed_folder:
                continue

            self.add_path(path, save_data=True)

        self.update_total_stocks()
        self.stocks.refresh_stocks(clear=True)

    def check(self):
        ffmpeg, ffprobe = get_ffmpeg()
        if not ffmpeg or not ffprobe:
            nuke.message(
                'You need to install <b>ffmpeg</b> and <b>ffprobe</b> to index !')
            return

        image_magick = '/usr/bin/identify'
        if not os.path.isfile(image_magick):
            nuke.message('Image Magick: not found "{}"'.format(image_magick))
            return

        return True

    def refresh_indexs(self):
        if not self.check():
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

    def each_folder_index(self, folder, amount, status):
        item = self.get_item(folder)
        if not item:
            return

        self.update_item(item, status, amount)

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

    def update_item(self, item, status, amount=-1):
        if not amount == -1:
            item.setText(1, str(amount))

        label = self.tree.itemWidget(item, 2)

        if not label:
            label = QLabel()
            self.tree.setItemWidget(item, 2, label)

        if status == -1:
            label.setStyleSheet('QLabel {color: rgb(255, 255, 0);}')
            label.setText('Indexing...')
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

    def add_path(self, path, indexed=False, amount=0, save_data=False):
        item = QTreeWidgetItem()
        basename = os.path.basename(path)

        item.setText(0, basename)
        item.setText(1, str(amount))

        for i in [0, 1, 2]:
            item.setToolTip(
                i, 'The folder containing the name <b>"texture"</b>\nwill ignore all sequences in folder !')

        self.tree.addTopLevelItem(item)
        self.update_item(item, indexed, amount)

        if save_data:
            indexing.save_indexed_folder(basename)

    def get_item(self, path):
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if path == item.text(0):
                return item

        return None

