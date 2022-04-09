import socket
import PyQt5.QtCore as QtCore
from core.VideoWorker import VideoWorker
from core.TDDFA import TDDFAPredictionContainer


class RemoteVideoWorker(VideoWorker):
    connectionEstablishedSignal = QtCore.pyqtSignal(str)
    connectionClosedSignal = QtCore.pyqtSignal(str)
    packetReceivedSignal = QtCore.pyqtSignal(TDDFAPredictionContainer)

    def __init__(self, address):
        super(RemoteVideoWorker, self).__init__()
        self.connectionEstablishedSignal.connect(self.receive)
        self.server_port = 45005
        self.client_port = 45015
        self.server_socket = None
        self.client_socket = None
        self.server_connection = None
        self.client_connection = None
        self.client_address = address
        self.packet_buffer = b""

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
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("", self.server_port))

    @QtCore.pyqtSlot(str)
    def receive(self, address):
        self.server_socket.listen(1)
        connection, r_address = self.server_socket.accept()
        while address != r_address:
            connection, r_address = self.server_socket.accept()
        while connection:
            packet = self.read_packet(connection)
            frames = packet.decode()
            for frame in frames:
                self.packetReceivedSignal.emit(frame)

    @QtCore.pyqtSlot()
    def connect(self):
        self.connectionEstablishedSignal.emit(self.client_address)
        self.client_socket.connect((self.client_address, self.server_port))

    @QtCore.pyqtSlot(TDDFAPredictionContainer)
    def send_packet(self, packet: TDDFAPredictionContainer):
        try:
            self.client_socket.sendall(packet.encode())
        except:
            pass

    @QtCore.pyqtSlot()
    def close_connection(self):
        self.client_socket.close()
        self.server_socket.close()
