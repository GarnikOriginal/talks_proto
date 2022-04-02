from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow
from widgets.main import Ui_MainWindow
from core.TDDFA import TDDFAPredictionContainer
from core.LocalCameraWorker import LocalCameraWorker
from core.RemoteVideoWorker import RemoteVideoWorker
from common.VideoContainer import VideoContainer


class MainForm(QMainWindow, Ui_MainWindow):
    send_packet = QtCore.pyqtSignal(TDDFAPredictionContainer)

    def __init__(self, app, loop):
        super(MainForm, self).__init__()
        self.app = app
        self.loop = loop
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
        self.local_video.setMaximumWidth(self.gridLayoutConference.widget().width() / 2)
        self.gridLayoutConference.addWidget(self.local_video, 1, 1, 1, 1)
        self.local_video.show()
        self.pushButtonLocalCamera.setEnabled(False)
        self.pushButtonOpenConection.setEnabled(True)

    @QtCore.pyqtSlot(str)
    def connection_established(self, address: str):
        print(f"SLOT connection_established: {address}")
        self.remote_video = VideoContainer(self.remote_video)
        self.remote_video.setMaximumWidth(self.gridLayoutConference.widget().width() / 2)
        self.local_video.worker.packetReady.connect(self.remote_video.worker.send_packet)
        self.gridLayoutConference.addWidget(self.remote_video, 1, 2, 1, 1)
        self.remote_video.show()

    @QtCore.pyqtSlot()
    def open_connection(self):
        worker = RemoteVideoWorker()
        worker.connectionEstablished.connect(self.connection_established)
        thread = QtCore.QThread(parent=self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        thread.start()
        self.threads.append(thread)
        self.pushButtonOpenConection.setEnabled(False)
        self.pushButtonConnect.setEnabled(True)

    @QtCore.pyqtSlot()
    def establish_connection(self):
        pass

    def setup_callbacks(self):
        self.pushButtonLocalCamera.clicked.connect(self.set_local_stream)
        self.pushButtonOpenConection.clicked.connect(self.open_connection)
        self.pushButtonConnect.clicked.connect(self.establish_connection)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.local_video:
            self.local_video.worker.stream.camera.close()
