import av
import json
import zlib
import pickle
import socket
import PyQt5.QtCore as QtCore
from PyQt5.QtGui import QPixmap
from common.Telemetry import Telemetry
from core.VideoWorker import VideoWorker
from core.TDDFA import __uv_text_size__, __yuv420p__
from core.сore import server_port


class RemoteVideoReceiver(VideoWorker):
    updateTrafficSignal = QtCore.pyqtSignal(int, int)
    updateOutputFPSSignal = QtCore.pyqtSignal(int)
    frameReadySignal = QtCore.pyqtSignal(QPixmap)
    connectionClosed = QtCore.pyqtSignal(str)

    def __init__(self, address):
        super(RemoteVideoReceiver, self).__init__()
        self.address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.telemetry = Telemetry()
        self.config = None
        self.bg_decoder = None
        self.bg_decoder_context = None
        self.uv_decoder = None
        self.uv_decoder_context = None
        self.config_received = False
        self.buffer = b""
        self.message_size = -1

    def run(self):
        self.socket.bind(("", server_port))
        self.socket.listen(1)
        connection, r_address = self.socket.accept()
        packet = self.read_config(connection)
        h, w = self.config["video_size"].split("x")
        self.config["w"] = int(w)
        self.config["h"] = int(h)
        self.create_decoders()
        while connection:
            while len(packet) < 4:
                packet += connection.recv(4096)
            size_bytes, packet = packet[0:4], packet[4:]
            self.message_size = int.from_bytes(size_bytes, byteorder='big')
            while len(packet) < self.message_size:
                packet += connection.recv(4096)
            self.buffer, packet = packet[0:self.message_size], packet[self.message_size:]
            self.telemetry.step_traffic(len(self.buffer) / 1024)
            self.buffer = zlib.decompress(self.buffer)
            frames = pickle.loads(self.buffer).decode(self.bg_decoder_context,
                                                      self.uv_decoder_context,
                                                      (self.config["h"], self.config["w"]))
            for frame in frames:
                self.telemetry.step_frame()
                self.frameReadySignal.emit(frame)
            self.buffer = b""
            self.message_size = -1
            if self.telemetry.stats_ready():
                traffic, total_traffic, fps = self.telemetry.get_stats()
                self.updateTrafficSignal.emit(traffic, total_traffic)
                self.updateOutputFPSSignal.emit(fps)
        self.socket.close()
        self.connectionClosed.emit(self.address)

    def read_config(self, connection):
        packet = connection.recv(4096)
        while len(packet) < 4:
            packet += connection.recv(4096)
        config_size, packet = packet[0:4], packet[4:]
        config_size = int.from_bytes(config_size, byteorder='big')
        while len(packet) < config_size:
            packet += connection.recv(4096)
        config, tail = packet[0:config_size], packet[config_size:]
        config = config.decode("utf8")
        self.config = json.loads(config)
        return tail

    def create_decoders(self):
        h, w = self.config["h"], self.config["w"]
        self.bg_decoder, self.bg_decoder_context = self.create_decoder(h // self.config["bg_scale"],
                                                                       w // self.config["bg_scale"],
                                                                       int(self.config["framerate"]))
        self.uv_decoder, self.uv_decoder_context = self.create_decoder(__uv_text_size__,
                                                                       __uv_text_size__,
                                                                       int(self.config["framerate"]))

    @staticmethod
    def create_decoder(h, w, framerate):
        decoder = av.codec.Codec("mpeg4", "r")
        context = decoder.create()
        context.format = __yuv420p__
        context.framerate = framerate
        context.height = h
        context.width = w
        return decoder, context

