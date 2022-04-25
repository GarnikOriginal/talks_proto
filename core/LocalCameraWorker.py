import torch
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QImage
from core.VideoWorker import TDDFAVideoWorker
from core.TDDFA import TDDFAWrapper, TDDFAPredictionContainer
from core.CameraStream import CameraStream


class LocalCameraWorker(TDDFAVideoWorker):
    def __init__(self, config):
        super(LocalCameraWorker, self).__init__()
        self.stream = CameraStream(config)
        self.camera_context = self.stream.config
        self.scale_factor = config["bg_scale"]
        self.tddfa = TDDFAWrapper((self.stream.coded_width // self.scale_factor,
                                   self.stream.coded_height // self.scale_factor))
        self.running = True

    def run(self):
        torch.set_grad_enabled(False)
        if self.camera_context["use_tddfa"]:
            self.process_with_tddfa()
        else:
            self.process_without_tddfa()

    def process_with_tddfa(self):
        while self.running:
            for packet in self.stream.get_current_package():
                for frame in packet.decode():
                    frame = frame.to_ndarray(format='rgb24')
                    self.tddfa.forward(frame)
                    image = QImage(frame, frame.shape[1], frame.shape[0], frame.shape[1] * 3, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(image)
                    self.frameReadySignal.emit(pixmap)
                self.packetReadySignal.emit(self.tddfa.pop_packet())
        self.stream.close()

    def process_without_tddfa(self):
        while self.running:
            for packet in self.stream.get_current_package():
                for frame in packet.decode():
                    frame = frame.to_ndarray(format='rgb24')
                    image = QImage(frame, frame.shape[1], frame.shape[0], frame.shape[1] * 3, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(image)
                    self.frameReadySignal.emit(pixmap)
                    self.packetReadySignal.emit(TDDFAPredictionContainer(background={0: frame},
                                                                         uv_textures={},
                                                                         roi_boxes={},
                                                                         deep_features={}))
        self.stream.close()
