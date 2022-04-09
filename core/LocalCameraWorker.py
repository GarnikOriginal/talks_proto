import torch
from PyQt5.QtGui import QPixmap, QImage
from core.VideoWorker import TDDFAVideoWorker
from core.TDDFA import TDDFAWrapper
from core.CameraStream import CameraStream


class LocalCameraWorker(TDDFAVideoWorker):
    def __init__(self):
        super(LocalCameraWorker, self).__init__()
        self.stream = CameraStream()
        self.tddfa = TDDFAWrapper((self.stream.coded_width // 4, self.stream.coded_height // 4))

    def run(self):
        torch.set_grad_enabled(False)
        while True:
            for packet in self.stream.get_current_package():
                for frame in packet.decode():
                    frame = frame.to_ndarray(format='rgb24')
                    self.tddfa.forward(frame)
                    image = QImage(frame, frame.shape[1], frame.shape[0], frame.shape[1] * 3, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(image)
                    self.frameReadySignal.emit(pixmap)
                self.packetReadySignal.emit(self.tddfa.pop_packet())

    def __del__(self):
        del self.stream
