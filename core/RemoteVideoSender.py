import av
import json
import PyQt5.QtCore as QtCore
from core.VideoWorker import RemoteVideoWorker
from core.TDDFA import TDDFAPredictionContainer, __yuv420p__, __uv_text_w__, __uv_text_h__
from core.сore import server_port


class RemoteVideoSender(RemoteVideoWorker):
    def __init__(self, address, local_config):
        super(RemoteVideoSender, self).__init__(address, local_config)
        self.config_sent = False
        h, w = self.local_config["video_size"].split("x")
        self.bg_encoder, self.bg_encoder_contex = self.create_encoder(int(h) // self.local_config["bg_scale"],
                                                                      int(w) // self.local_config["bg_scale"],
                                                                      self.local_config["framerate"])
        self.uv_encoder, self.uv_encoder_contex = self.create_encoder(__uv_text_h__,
                                                                      __uv_text_w__,
                                                                      self.local_config["framerate"])

    def run(self):
        while self.socket.connect_ex((self.address, server_port)) and self.running:
            pass

    @QtCore.pyqtSlot(TDDFAPredictionContainer)
    def send_packet(self, packet: TDDFAPredictionContainer):
        try:
            if not self.config_sent:
                self.send_conf()
            packet = packet.encode(self.bg_encoder_contex, self.uv_encoder_contex)
            size = len(packet)
            prefix = size.to_bytes(4, byteorder='big')
            packet = prefix + packet
            self.socket.sendall(packet)
            self.telemetry.step_traffic(size / 1024)
            self.telemetry.step_frame()
            if self.telemetry.stats_ready():
                traffic, per_frame, total_traffic, fps = self.telemetry.get_stats()
                self.updateTrafficSignal.emit(traffic, per_frame, total_traffic)
                self.updateOutputFPSSignal.emit(fps)
        except Exception as err:
            raise err

    def send_conf(self):
        conf = json.dumps(self.local_config)
        conf = bytes(conf, encoding="utf8")
        size = len(conf).to_bytes(4, byteorder='big')
        conf = size + conf
        self.socket.sendall(conf)
        self.config_sent = True

    @staticmethod
    def create_encoder(h, w, framerate):
        encoder = av.codec.Codec("mpeg4", "w")
        context = encoder.create()
        context.format = __yuv420p__
        context.framerate = framerate
        context.height = h
        context.width = w
        return encoder, context
