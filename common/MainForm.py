from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow
from widgets.main import Ui_MainWindow
from core.TDDFA import TDDFAPredictionContainer
from core.LocalCameraWorker import LocalCameraWorker
from core.RemoteVideoSender import RemoteVideoSender
from core.RemoteVideoReceiver import RemoteVideoReceiver
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
        self.local_video_container = None
        self.remote_video_container = None
        self.threads = []
        self.remote_senders = []
        self.remote_receivers = []
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
        self.local_video_container = VideoContainer(worker)
        self.local_video_container.setMaximumWidth(self.stream_width)
        self.gridLayoutConference.addWidget(self.local_video_container, 1, 1, 1, 1)
        self.local_video_container.show()
        self.pushButtonLocalCamera.setEnabled(False)
        self.enable_connect_controls(True)

    @QtCore.pyqtSlot()
    def disconnect(self):
        self.enable_connect_controls(True)
        self.pushButtonDisconnect.setEnabled(False)

    @QtCore.pyqtSlot()
    def connect(self):
        ip = self.lineEditConnectionIP.text()
        receiver_worker = RemoteVideoReceiver(ip)
        receiver_thread = QtCore.QThread(parent=self)
        receiver_worker.moveToThread(receiver_thread)
        receiver_thread.started.connect(receiver_worker.run)
        self.remote_video_container = VideoContainer(receiver_worker)
        receiver_thread.start()
        self.threads.append(receiver_thread)
        self.remote_receivers.append(receiver_worker)

        sender_worker = RemoteVideoSender(ip, self.local_video_container.worker.camera_context)
        sender_thread = QtCore.QThread(parent=self)
        sender_worker.moveToThread(sender_thread)
        sender_thread.started.connect(sender_worker.run)
        self.local_video_container.worker.packetReadySignal.connect(sender_worker.send_packet)
        self.pushButtonDisconnect.clicked.connect(sender_worker.close_connection)
        sender_thread.start()
        self.threads.append(sender_thread)
        self.remote_senders.append(sender_worker)

        self.remote_video_container.setMaximumWidth(self.stream_width)
        self.gridLayoutConference.addWidget(self.remote_video_container, 1, 2, 1, 1)
        self.remote_video_container.show()
        self.enable_connect_controls(False)
        self.pushButtonDisconnect.setEnabled(True)
        self.pushButtonDisconnect.clicked.connect(self.disconnect)
        self.connectSignal.emit()

    def enable_connect_controls(self, state):
        self.pushButtonConnect.setEnabled(state)
        self.lineEditConnectionIP.setEnabled(state)

    def setup_callbacks(self):
        self.pushButtonLocalCamera.clicked.connect(self.set_local_stream)
        self.pushButtonConnect.clicked.connect(self.connect)
        self.pushButtonDisconnect.clicked.connect(self.disconnect)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.local_video_container:
            self.local_video_container.worker.stream.camera.close()
