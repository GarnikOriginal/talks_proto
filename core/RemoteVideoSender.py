import socket
import PyQt5.QtCore as QtCore
from core.TDDFA import TDDFAPredictionContainer
from core.сore import server_port


class RemoteVideoSender(QtCore.QObject):
    def __init__(self, address):
        super(RemoteVideoSender, self).__init__()
        self.address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.socket.connect((self.address, server_port))

    @QtCore.pyqtSlot(TDDFAPredictionContainer)
    def send_packet(self, packet: TDDFAPredictionContainer):
        try:
            self.socket.sendall(packet.encode())
        except:
            pass

    @QtCore.pyqtSlot()
    def close_connection(self):
        self.socket.close()
