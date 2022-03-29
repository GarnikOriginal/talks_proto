import PyQt5.QtCore as QtCore
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel

from .LocalStream import LocalStream
from .VideoStream import VideoStream


class VideoWorker(QObject):
    frameReady = pyqtSignal(QPixmap, str)

    def __init__(self, source: str, name: str):
        super(VideoWorker, self).__init__()
        self.name = name
        self.stream = LocalStream(source)

    def run(self):
        while True:
            for packet in self.stream.get_current_package():
                for frame in packet.decode():
                    frame = frame.to_ndarray(format='rgb24')
                    image = QImage(frame, frame.shape[1], frame.shape[0], frame.shape[1] * 3, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(image)
                    self.frameReady.emit(pixmap, self.name)

    def __del__(self):
        del self.stream


class VideoOutputContainer:
    def __init__(self, name: str, worker: VideoWorker, thread: QtCore.QThread, label:QLabel):
        self.name = name
        self.worker = worker
        self.thread = thread
        self.label = label
