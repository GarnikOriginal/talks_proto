import socket
import PyQt5.QtCore as QtCore
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel
from core.VideoWorker import VideoWorker
from core.TDDFA import TDDFAPredictionContainer


class RemoteVideoWorker(VideoWorker):
    connectionEstablished = QtCore.pyqtSignal(str)
    connectionClosed = QtCore.pyqtSignal(str)

    def __init__(self):
        super(RemoteVideoWorker, self).__init__()
        self.port = 45005
        self.packet_buffer = b""
        self.connection = None

    def read_packet(self, connection):
        while True:
            data, address = connection.recvfrom(4096)
            if not data:
                packet = self.packet_buffer
                self.packet_buffer = b""
                return packet
            else:
                self.packet_buffer += data

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", self.port))
            s.listen(1)
            connection, address = socket.accept()
            print('Take connection by', address)
            with connection:
                self.connection = connection
                self.connectionEstablished.emit(self, address)
                while True:
                    packet = self.read_packet(connection)
                    # TODO: DECODE
                    # self.frameReady.emit(frame)
                    print(f"PACKET RECIVED: {packet} from {address}")

    @QtCore.pyqtSlot(TDDFAPredictionContainer)
    def send_packet(self, packet: TDDFAPredictionContainer):
        if self.connection:
            self.connection.sendall(b"TRY SEND")
        else:
            print("Error: connection closed")
