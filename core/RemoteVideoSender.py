import av
import json
import socket
import PyQt5.QtCore as QtCore
from common.Telemetry import Telemetry
from core.TDDFA import TDDFAPredictionContainer
from core.сore import server_port


class RemoteVideoSender(QtCore.QObject):
    updateTrafficSignal = QtCore.pyqtSignal(int, int)
    updateOutputFPSSignal = QtCore.pyqtSignal(int)

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
        self.telemetry = Telemetry()

    def run(self):
        while self.socket.connect_ex((self.address, server_port)):
            pass

    @QtCore.pyqtSlot(TDDFAPredictionContainer)
    def send_packet(self, packet: TDDFAPredictionContainer):
        try:
            if not self.config_sent:
                self.send_conf()
            packet = packet.encode(self.encoder_contex)
            size = len(packet)
            prefix = size.to_bytes(4, byteorder='big')
            packet = prefix + packet
            self.socket.sendall(packet)
            self.telemetry.step_traffic(size / 1024)
            self.telemetry.step_frame()
            if self.telemetry.stats_ready():
                traffic, total_traffic, fps = self.telemetry.get_stats()
                self.updateTrafficSignal.emit(traffic, total_traffic)
                self.updateOutputFPSSignal.emit(fps)
        except Exception as err:
            print(err)

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
