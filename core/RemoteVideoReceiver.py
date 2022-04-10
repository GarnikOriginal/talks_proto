import av
import json
import zlib
import pickle
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
        self.config = None
        self.decoder = None
        self.decoder_context = None
        self.config_received = False
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
                while len(self.buffer) < self.message_size:
                    packet = connection.recv(4096)
                    self.buffer += packet
                packet = self.buffer[self.message_size:]
                self.buffer = self.buffer[0:self.message_size]
                if self.config_received:
                    print("Get frame")
                    self.buffer = zlib.decompress(self.buffer)
                    frames = pickle.loads(self.buffer).decode(self.decoder_context)
                    for frame in frames:
                        self.frameReadySignal.emit(frame)
                else:
                    config = self.buffer.decode("utf8")
                    self.config = json.loads(config)
                    print(f"Get config: {self.config}")
                    self.config_received = True
                    self.create_decoder()
                self.size_buffer = b""
                self.buffer = b""
                self.message_size = -1
        self.socket.close()
        self.connectionClosed.emit(self.address)

    def create_decoder(self):
        decoder = av.codec.Codec("mpeg4", "r")
        context = decoder.create()
        context.format = av.video.format.VideoFormat("yuv420p")
        context.framerate = self.config["framerate"]
        h, w = self.config["video_size"].split("x")
        context.height = int(h) // 10
        context.width = int(w) // 10
        self.decoder = decoder
        self.decoder_context = context
