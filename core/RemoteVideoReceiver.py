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
        self.size_buffer = b""
        self.buffer = b""
        self.message_size = -1

    def run(self):
        self.socket.bind(("", server_port))
        self.socket.listen(1)
        connection, r_address = self.socket.accept()
        packet = b""
        while connection:
            if packet == b"":
                packet = connection.recv(4096)
            if len(self.size_buffer) < 4:
                if len(packet) < 4:
                    self.size_buffer += packet
                    continue
                else:
                    self.size_buffer += packet[0:4 - (len(self.size_buffer))]
                    packet = packet[(len(self.size_buffer)):]
            else:
                self.message_size = int.from_bytes(self.size_buffer, byteorder='big')
                self.buffer += packet
                while len(self.buffer) != self.message_size:
                    packet = connection.recv(4096)
                    if len(self.buffer) + len(packet) < self.message_size:
                        self.buffer += packet
                    else:
                        tail_size = self.message_size - len(self.buffer)
                        self.buffer += packet[0:tail_size]
                        packet = packet[tail_size:]
                frames = self.buffer.decode()
                for frame in frames:
                    self.frameReadySignal.emit(frame)
                self.size_buffer = b""
                self.message_size = -1
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
