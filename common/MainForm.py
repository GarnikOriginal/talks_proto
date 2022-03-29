import os
import PyQt5.QtCore as QtCore
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMainWindow, QLabel, QLayoutItem
from .LocalStream import LocalStream
from .VideoOutput import VideoWorker, VideoOutputContainer
from widgets.main import Ui_MainWindow


class MainForm(QMainWindow, Ui_MainWindow):
    def __init__(self, app, loop):
        super(MainForm, self).__init__()
        self.app = app
        self.loop = loop
        self.setupUi(self)
        self.setup_callbacks()
        self.active_video_outputs = {}

    def __del__(self):
        for output in self.active_video_outputs.values():
            print(f"deleted {output.name}")
            output.thread.exit()

    @QtCore.pyqtSlot()
    def set_local_stream(self):
        label = QLabel()
        self.gridLayoutConference.setSpacing(1)
        self.gridLayoutConference.addWidget(label, 1, 1)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setScaledContents(True)
        label.setMinimumSize(1, 1)
        label.show()

        worker = VideoWorker("/dev/video0", "local")
        worker.frameReady.connect(self.update_frame)
        thread = QtCore.QThread()
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        thread.start()
        self.active_video_outputs["local"] = VideoOutputContainer("local", worker, thread, label)
        self.pushButtonLocalTest.setEnabled(False)

    @QtCore.pyqtSlot(QPixmap, str)
    def update_frame(self, pixmap: QPixmap, name: str):
        self.active_video_outputs[name].label.setPixmap(pixmap)
        self.active_video_outputs[name].label.adjustSize()

    def setup_callbacks(self):
        self.pushButtonLocalTest.clicked.connect(self.set_local_stream)
