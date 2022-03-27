import os
import PyQt5.QtCore as QtCore
from datetime import datetime
from asyncio import Lock
from asyncqt import asyncSlot, asyncClose
from PyQt5.QtCore import Qt, QSize, QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem, QWidget, QMessageBox, QAbstractItemView
from .LocalStream import LocalStream
from widgets.main import Ui_MainWindow


class MainForm(QMainWindow, Ui_MainWindow):
    def __init__(self, app, loop):
        super(MainForm, self).__init__()
        self.app = app
        self.loop = loop
        self.setupUi(self)
        self.camera = LocalStream()
        self.setup_callbacks()

    @QtCore.pyqtSlot()
    def set_local_stream(self):
        pass

    def setup_callbacks(self):
        self.pushButtonLocalTest.clicked.connect(self.set_local_stream)
