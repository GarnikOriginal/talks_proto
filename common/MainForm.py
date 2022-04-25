import sys
sys.path.append("./modules/TDDFA_V2")

from time import sleep
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow
from widgets.main import Ui_MainWindow
from common.VideoContainer import VideoContainer
from core.TDDFA import TDDFAPredictionContainer
from core.LocalCameraWorker import LocalCameraWorker
from core.RemoteVideoSender import RemoteVideoSender
from core.RemoteVideoReceiver import RemoteVideoReceiver


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
        self.threads = {}
        self.remote_senders = []
        self.remote_receivers = []
        ipRange = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        ipRegex = QtCore.QRegExp("^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$")
        ipValidator = QtGui.QRegExpValidator(ipRegex, self)
        self.lineEditConnectionIP.setValidator(ipValidator)

    @QtCore.pyqtSlot()
    def set_local_stream(self):
        camera_config = self.get_camera_config()
        self.enable_camera_settings(False)
        worker = LocalCameraWorker(camera_config)
        thread = QtCore.QThread(parent=self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        thread.start()
        self.threads["local"] = thread
        self.local_video_container = VideoContainer(worker)
        self.local_video_container.setMaximumWidth(self.stream_width)
        self.gridLayoutConference.addWidget(self.local_video_container, 1, 1, 1, 1)
        self.local_video_container.show()
        self.pushButtonLocalCamera.setEnabled(False)
        self.enable_connect_controls(True)

    @QtCore.pyqtSlot()
    def connect(self):
        ip = self.lineEditConnectionIP.text()
        receiver_worker = RemoteVideoReceiver(ip, self.local_video_container.worker.camera_context)
        receiver_thread = QtCore.QThread(parent=self)
        receiver_worker.moveToThread(receiver_thread)
        receiver_worker.updateTrafficSignal.connect(self.update_input_traffic_info)
        receiver_worker.updateOutputFPSSignal.connect(self.update_input_fps_info)
        receiver_thread.started.connect(receiver_worker.run)

        self.remote_video_container = VideoContainer(receiver_worker)
        receiver_thread.start()
        self.threads["receiver"] = receiver_thread
        self.remote_receivers.append(receiver_worker)

        sender_conf = self.local_video_container.worker.camera_context.copy()
        sender_conf["write_log"] = False
        sender_worker = RemoteVideoSender(ip, sender_conf)
        sender_thread = QtCore.QThread(parent=self)
        sender_worker.moveToThread(sender_thread)
        sender_thread.started.connect(sender_worker.run)
        sender_worker.updateTrafficSignal.connect(self.update_out_traffic_info)
        sender_worker.updateOutputFPSSignal.connect(self.update_out_fps_info)
        self.local_video_container.worker.packetReadySignal.connect(sender_worker.send_packet)
        sender_thread.start()
        self.threads["sender"] = sender_thread
        self.remote_senders.append(sender_worker)

        self.remote_video_container.setMaximumWidth(self.stream_width)
        self.gridLayoutConference.addWidget(self.remote_video_container, 1, 2, 1, 1)
        self.remote_video_container.show()
        self.enable_connect_controls(False)
        self.pushButtonDisconnect.setEnabled(True)
        self.pushButtonDisconnect.clicked.connect(self.disconnect)
        self.connectSignal.emit()

    @QtCore.pyqtSlot(int, float, int)
    def update_out_traffic_info(self, current, per_frame, total):
        self.labelTotalTrafficValue.setText(str(total))
        self.labelKBFrameOutValue.setText(str(round(per_frame, 2)))
        self.labelTrafficValue.setText(str(current))

    @QtCore.pyqtSlot(int)
    def update_out_fps_info(self, current):
        self.labelOutFpsValue.setText(str(current))

    @QtCore.pyqtSlot(int, float, int)
    def update_input_traffic_info(self, current, per_frame, total):
        self.labelTotalInputTrafficValue.setText(str(total))
        self.labelKBFrameInValue.setText(str(round(per_frame, 2)))
        self.labelInputTrafficValue.setText(str(current))

    @QtCore.pyqtSlot(int)
    def update_input_fps_info(self, current):
        self.labelInputFpsValue.setText(str(current))

    def get_camera_config(self):
        config = {
            "bg_scale": int(self.comboBoxBgScale.currentText()),
            "video_size": self.comboBoxResulution.currentText(),
            "framerate": int(self.comboBoxFPS.currentText()),
            "name": "/dev/video0",
            "use_tddfa": self.checkBoxUseTDDFA.isChecked(),
            "write_log": self.checkBoxWriteLog.isChecked()
        }
        return config

    def enable_camera_settings(self, enable=False):
        self.comboBoxBgScale.setEnabled(enable)
        self.comboBoxResulution.setEnabled(enable)
        self.comboBoxFPS.setEnabled(enable)
        self.checkBoxUseTDDFA.setEnabled(enable)
        self.checkBoxWriteLog.setEnabled(enable)

    def enable_connect_controls(self, state):
        self.pushButtonConnect.setEnabled(state)
        self.lineEditConnectionIP.setEnabled(state)

    def setup_callbacks(self):
        self.pushButtonLocalCamera.clicked.connect(self.set_local_stream)
        self.pushButtonConnect.clicked.connect(self.connect)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.local_video_container:
            self.local_video_container.worker.running = False
        if self.remote_senders:
            self.remote_senders[0].running = False
        if self.remote_receivers:
            self.remote_receivers[0].running = False
        sleep(0.5)
