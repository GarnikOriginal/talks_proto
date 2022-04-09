import socket
import PyQt5.QtCore as QtCore
from core.VideoWorker import VideoWorker
from core.TDDFA import TDDFAPredictionContainer


class RemoteVideoWorker(VideoWorker):
    connectionEstablishedSignal = QtCore.pyqtSignal(str)
    connectionClosedSignal = QtCore.pyqtSignal(str)
    packetReceivedSignal = QtCore.pyqtSignal(TDDFAPredictionContainer)

    def __init__(self):
        super(RemoteVideoWorker, self).__init__()
        self.port = 45005
        self.packet_buffer = b""
        self.socket = None
        self.connection = None
        self.address = None

    def read_packet(self):
        while True:
            data, address = self.connection.recvfrom(4096)
            if not data:
                packet = self.packet_buffer
                self.packet_buffer = b""
                return packet
            else:
                self.packet_buffer += data

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("", self.port))
        self.socket.listen(1)
        self.connection, self.address = self.socket.accept()
        self.connectionEstablishedSignal.emit(self, self.address)
        while self.connection:
            packet = self.read_packet()
            frames = packet.decode()
            for frame in frames:
                self.packetReceivedSignal.emit(frame)

    @QtCore.pyqtSlot(str)
    def connect(self, address):
        print(f"Try connect to: {address}")
        try:
            self.socket.connect((address, self.port))
        except Exception as error:
            print(f"Cant connect to {address}")

    @QtCore.pyqtSlot()
    def close_connection(self):
        self.connection.close()
        self.socket.close()

    @QtCore.pyqtSlot(TDDFAPredictionContainer)
    def send_packet(self, packet: TDDFAPredictionContainer):
        if self.connection:
            self.connection.sendall(packet.encode())
        else:
            self.connectionClosedSignal.emit(self.address)


