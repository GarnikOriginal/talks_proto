from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow
from common.VideoContainer import VideoContainer
from core.LocalCameraWorker import LocalCameraWorker
from core.TDDFA import TDDFAPredictionContainer
from widgets.main import Ui_MainWindow


class MainForm(QMainWindow, Ui_MainWindow):
    send_packet = QtCore.pyqtSignal(TDDFAPredictionContainer)

    def __init__(self, app, loop):
        super(MainForm, self).__init__()
        self.app = app
        self.loop = loop
        self.setupUi(self)
        self.setup_callbacks()
        self.local_video = None
        self.remote_video_containers = {}
        self.threads = []
        ipRange = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        ipRegex = QtCore.QRegExp("^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$")
        ipValidator = QtGui.QRegExpValidator(ipRegex, self)
        self.lineEditConnectionIP.setValidator(ipValidator)

    @QtCore.pyqtSlot()
    def set_local_stream(self):
        worker = LocalCameraWorker()
        worker.packetReady.connect(self.broadcast_packet)
        thread = QtCore.QThread(parent=self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        thread.start()
        self.threads.append(thread)
        self.local_video = VideoContainer(worker)
        self.gridLayoutConference.addWidget(self.local_video, 1, 1)
        self.local_video.show()
        self.pushButtonLocalCamera.setEnabled(False)
        self.pushButtonConnect.setEnabled(True)
        self.lineEditConnectionIP.setEnabled(True)

    @QtCore.pyqtSlot()
    def establish_connection(self):
        ip = self.lineEditConnectionIP.text()
        worker = self.local_video.worker
        container = VideoContainer(worker)
        self.gridLayoutConference.addWidget(container, 1, 2)
        self.remote_video_containers[ip] = container
        container.show()

    @QtCore.pyqtSlot(TDDFAPredictionContainer)
    def broadcast_packet(self, packet: TDDFAPredictionContainer):
        pass

    @QtCore.pyqtSlot()
    def setup_callbacks(self):
        self.pushButtonLocalCamera.clicked.connect(self.set_local_stream)
        self.pushButtonConnect.clicked.connect(self.establish_connection)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.local_video:
            self.local_video.worker.stream.camera.close()
