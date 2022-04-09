from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow
from widgets.main import Ui_MainWindow
from core.TDDFA import TDDFAPredictionContainer
from core.LocalCameraWorker import LocalCameraWorker
from core.RemoteVideoWorker import RemoteVideoWorker
from common.VideoContainer import VideoContainer


class MainForm(QMainWindow, Ui_MainWindow):
    sendPacketSignal = QtCore.pyqtSignal(TDDFAPredictionContainer)
    connectSignal = QtCore.pyqtSignal()

    def __init__(self, app, loop):
        super(MainForm, self).__init__()
        self.app = app
        self.loop = loop
        self.stream_width = 640
        self.setupUi(self)
        self.setup_callbacks()
        self.local_video = None
        self.remote_video = None
        self.threads = []
        ipRange = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        ipRegex = QtCore.QRegExp("^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$")
        ipValidator = QtGui.QRegExpValidator(ipRegex, self)
        self.lineEditConnectionIP.setValidator(ipValidator)

    @QtCore.pyqtSlot()
    def set_local_stream(self):
        worker = LocalCameraWorker()
        thread = QtCore.QThread(parent=self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        thread.start()
        self.threads.append(thread)
        self.local_video = VideoContainer(worker)
        self.local_video.setMaximumWidth(self.stream_width)
        self.gridLayoutConference.addWidget(self.local_video, 1, 1, 1, 1)
        self.local_video.show()
        self.pushButtonLocalCamera.setEnabled(False)
        self.enable_connect_controls(True)

    @QtCore.pyqtSlot(str)
    def connection_established(self, address: str):
        self.lineEditConnectionIP.setText(address)
        self.enable_connect_controls(False)

    @QtCore.pyqtSlot()
    def connect(self):
        ip = self.lineEditConnectionIP.text()
        worker = RemoteVideoWorker(ip)
        thread = QtCore.QThread(parent=self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        self.local_video.worker.packetReadySignal.connect(worker.send_packet)
        self.connectSignal.connect(worker.connect)
        thread.start()
        self.threads.append(thread)
        self.remote_video = VideoContainer(worker)
        self.remote_video.setMaximumWidth(self.stream_width)
        self.gridLayoutConference.addWidget(self.remote_video, 1, 2, 1, 1)
        self.remote_video.show()
        self.enable_connect_controls(False)
        self.connectSignal.emit()

    def enable_connect_controls(self, state):
        self.pushButtonConnect.setEnabled(state)
        self.lineEditConnectionIP.setEnabled(state)

    def setup_callbacks(self):
        self.pushButtonLocalCamera.clicked.connect(self.set_local_stream)
        self.pushButtonConnect.clicked.connect(self.connect)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.local_video:
            self.local_video.worker.stream.camera.close()
