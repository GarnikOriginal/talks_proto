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
        i = 0
        while connection:
            packet = self.read_packet(connection)
            frames = packet.decode()
            for frame in frames:
                self.frameReadySignal.emit(frame)
                print(f"Frame, packet: {i}")
            i += 1
        self.socket.close()
        self.connectionClosed.emit(self.address)

    def read_packet(self, connection):
        while True:
            data = connection.recv(4096)
            if data.endswith(rb'\q'):
                packet = self.buffer + data[0:-2]
                self.buffer = b""
                return packet
            else:
                self.buffer += data
