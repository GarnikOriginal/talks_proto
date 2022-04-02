import socket
import PyQt5.QtCore as QtCore
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel
from .LocalCameraWorker import TDDFAPredictionContainer


class RemoteVideoConnection(QtCore.QObject):
    packet_received = pyqtSignal(TDDFAPredictionContainer)
    def __init__(self):
        super(RemoteVideoConnection, self).__init__()
        self.socket_addr = "localhost:40015"

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(self.socket_addr)
            while True:
                s.listen(1)
                conn, addr = socket.accept()
                with conn:
                    data = conn.recv(62 * 3 * 4 + )