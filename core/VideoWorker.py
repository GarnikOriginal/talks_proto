import PyQt5.QtCore as QtCore
from PyQt5.QtGui import QPixmap
from core.TDDFA import TDDFAPredictionContainer


class VideoWorker(QtCore.QObject):
    frameReady = QtCore.pyqtSignal(QPixmap)


class TDDFAVideoWorker(VideoWorker):
    packetReady = QtCore.pyqtSignal(TDDFAPredictionContainer)
