# Author: Francisco Jose Contreras Cuevas
# Office: VFX Artist - Senior Compositor
# Website: vinavfx.com
import os
import nuke
import threading

from . import indexing

from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTreeWidget, QTreeWidgetItem,
                               QFileDialog, QAbstractItemView, QTreeView)

class dirs_stock_view(QTreeWidget):
    def __init__(self, add_path):
        self.add_path = add_path
        QTreeWidget.__init__(self)

        self.setColumnCount(3)
        self.setColumnWidth(0, 150)
        self.setColumnWidth(1, 70)
        self.setColumnWidth(2, 150)

        self.setHeaderLabels(['Name', 'Amount', 'Path', 'Status'])
        self.setAlternatingRowColors(True)
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.MultiSelection)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
            folders = indexing.get_indexed_folder()

            for url in event.mimeData().urls():
                url = url.toLocalFile()

                if not url in folders:
                    self.add_path(url)
        else:
            event.ignore()


class dirs_stock(QWidget):
    def __init__(self, stocks, status_bar):
        QWidget.__init__(self)

        self.stocks = stocks
        self.status_bar = status_bar
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tree = dirs_stock_view(self.add_path)

        buttons_layout = QHBoxLayout()
        buttons_layout.setMargin(0)
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)

        self.add_button = QPushButton('+')
        self.add_button.clicked.connect(lambda: self.add_path_dialog())

        self.delete_btn = QPushButton('-')
        self.delete_btn.clicked.connect(lambda: self.delete_path())

        self.refresh_index_btn = QPushButton('Refresh Indexs')
        self.refresh_index_btn.clicked.connect(self.refresh_indexs)

        buttons_layout.addWidget(self.refresh_index_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addWidget(self.add_button)

        layout.addWidget(self.tree)
        layout.addWidget(buttons_widget)

        for folder, data in indexing.get_indexed_folder().items():
            self.add_path(folder, data['indexed'], data['amount'])

        self.update_total_stocks()


    def add_path_dialog(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)

        tree = dialog.findChild(QTreeView)
        tree.setSelectionMode(QAbstractItemView.MultiSelection)
        tree.setSelectionMode(QAbstractItemView.ExtendedSelection)

        if not dialog.exec_():
            return

        folders = indexing.get_indexed_folder()
        for path in dialog.selectedFiles():
            if not path in folders:
                self.add_path(path)

    def refresh_indexs(self):
        self.refresh_index_btn.setText('Stop')
        self.refresh_index_btn.clicked.disconnect()
        self.status_bar.set_indexing_stock('analyzing')

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
        self.add_button.setEnabled(False)
        self.delete_btn.setEnabled(False)

        indexing.to_index(self.finished_index,
                          self.each_folder_index, self.each_index, stop_threads)

    def each_index(self, f, folder, percent, indexed_stocks):
        item = self.get_item(folder)
        if not item:
            return

        self.status_bar.set_indexing_stock(f, percent)

        self.update_item(item, -1, indexed_stocks)
        self.update_total_stocks()

    def each_folder_index(self, folder, amount):
        item = self.get_item(folder)
        if not item:
            return

        self.update_item(item, 1, amount)

    def finished_index(self):
        self.add_button.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.refresh_index_btn.setText('Refresh Indexs')
        self.refresh_index_btn.clicked.disconnect()
        self.refresh_index_btn.clicked.connect(self.refresh_indexs)
        self.refresh_index_btn.setEnabled(True)

        self.status_bar.set_indexing_stock('finished')
        self.update_total_stocks()
        nuke.executeInMainThread(self.stocks.clear_and_refresh)

    def update_item(self, item, status, amount):
        item.setText(1, str(amount))

        status = status if os.path.isdir(item.text(2)) else -2

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
        self.status_bar.set_total_stocks(total_stocks)

    def add_path(self, path, indexed=False, amount=0):
        item = QTreeWidgetItem()

        item.setText(0, os.path.basename(path))
        item.setText(1, str(amount))
        item.setText(2, path)

        for i in [0, 1, 2]:
            item.setToolTip(
                i, 'The folder containing the name <b>"texture"</b>\nwill ignore all sequences in folder !')

        self.tree.addTopLevelItem(item)
        self.update_item(item, indexed, amount)

        if not indexed:
            indexing.save_indexed_folder(path)

    def get_item(self, path):
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if path == item.text(2):
                return item

        return None

    def delete_path(self):
        if not nuke.ask('Are you sure you want to delete {} folders ?'.format(len(self.tree.selectedItems()))):
            return

        root = self.tree.invisibleRootItem()
        for item in self.tree.selectedItems():
            indexing.delete_folder(item.text(2))
            (item.parent() or root).removeChild(item)
