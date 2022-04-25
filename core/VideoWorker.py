import socket
import PyQt5.QtCore as QtCore
from PyQt5.QtGui import QPixmap
from common.Telemetry import Telemetry
from core.TDDFA import TDDFAPredictionContainer


class VideoWorker(QtCore.QObject):
    frameReadySignal = QtCore.pyqtSignal(QPixmap)


class TDDFAVideoWorker(VideoWorker):
    packetReadySignal = QtCore.pyqtSignal(TDDFAPredictionContainer)


class RemoteVideoWorker(VideoWorker):
    updateTrafficSignal = QtCore.pyqtSignal(int, float, int)
    updateOutputFPSSignal = QtCore.pyqtSignal(int)
    connectionClosed = QtCore.pyqtSignal(str)

    def __init__(self, address, local_config):
        super(RemoteVideoWorker, self).__init__()
        self.running = True
        self.telemetry = Telemetry(local_config["write_log"])
        self.address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.local_config = local_config

