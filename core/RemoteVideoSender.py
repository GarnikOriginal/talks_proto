import av
import json
import socket
import PyQt5.QtCore as QtCore
from core.TDDFA import TDDFAPredictionContainer
from core.сore import server_port


class RemoteVideoSender(QtCore.QObject):
    def __init__(self, address, local_config):
        super(RemoteVideoSender, self).__init__()
        self.address = address
        self.local_config = local_config
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.config_sent = False
        self.encoder = av.codec.Codec("mpeg4", "w")
        self.encoder_contex = self.encoder.create()
        self.encoder_contex.format = av.video.format.VideoFormat("yuv420p")
        self.encoder_contex.framerate = self.local_config["framerate"]
        h, w = self.local_config["video_size"].split("x")
        self.encoder_contex.height = int(h)
        self.encoder_contex.width = int(w)

    def run(self):
        while self.socket.connect_ex((self.address, server_port)):
            pass

    @QtCore.pyqtSlot(TDDFAPredictionContainer)
    def send_packet(self, packet: TDDFAPredictionContainer):
        try:
            if not self.config_sent:
                self.send_conf()
                print(f"Send config: {self.local_config}")
            packet = packet.encode(self.encoder_contex)
            size = len(packet).to_bytes(4, byteorder='big')
            packet = size + packet
            self.socket.sendall(packet)
        except:
            pass

    def send_conf(self):
        conf = json.dumps(self.local_config)
        conf = bytes(conf, encoding="utf8")
        size = len(conf).to_bytes(4, byteorder='big')
        conf = size + conf
        self.socket.sendall(conf)
        self.config_sent = True

    @QtCore.pyqtSlot()
    def close_connection(self):
        self.socket.close()
