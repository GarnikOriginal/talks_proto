import PyQt5.QtCore as QtCore
from PyQt5.QtGui import QPixmap
from core.TDDFA import TDDFAPredictionContainer


class VideoWorker(QtCore.QObject):
    frameReadySignal = QtCore.pyqtSignal(QPixmap)


class TDDFAVideoWorker(VideoWorker):
    packetReadySignal = QtCore.pyqtSignal(TDDFAPredictionContainer)
