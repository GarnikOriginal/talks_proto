import socket
import PyQt5.QtCore as QtCore
from PyQt5.QtGui import QPixmap
from core.VideoWorker import VideoWorker
from core.сore import server_port


class RemoteVideoReceiver(VideoWorker):
    frameReadySignal = QtCore.pyqtSignal(QPixmap)
    connectionClosed = QtCore.pyqtSignal(str)

    def __init__(self, address):
        super(RemoteVideoReceiver, self).__init__()
        self.address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer = b""

    def run(self):
        self.socket.bind(("", server_port))
        self.socket.listen(1)
        connection, r_address = self.socket.accept()
        while connection:
            packet = self.read_packet(connection)
            frames = packet.decode()
            for frame in frames:
                self.frameReadySignal.emit(frame)
        self.socket.close()
        self.connectionClosed.emit(self.address)

    def read_packet(self, connection):
        while True:
            data, address = connection.recvfrom(4096)
            if not data:
                packet = self.buffer
                self.buffer = b""
                return packet
            else:
                self.buffer += data
