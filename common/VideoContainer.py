import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from core.VideoWorker import VideoWorker


class VideoContainer(QLabel):
    def __init__(self, worker: VideoWorker):
        super(VideoContainer, self).__init__()
        self.worker = worker
        self.worker.frameReady.connect(self.update_frame)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setScaledContents(True)
        self.setMinimumSize(1, 1)

    @QtCore.pyqtSlot(QPixmap)
    def update_frame(self, frame: QPixmap):
        print("Update frame")
        self.setPixmap(frame)
        self.adjustSize()
