
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMainWindow, QLabel, QLayoutItem
from .VideoOutput import VideoWorker, VideoOutputContainer
from .TDDFA import TDDFAPredictionContainer
from widgets.main import Ui_MainWindow


class MainForm(QMainWindow, Ui_MainWindow):
    def __init__(self, app, loop):
        super(MainForm, self).__init__()
        self.app = app
        self.loop = loop
        self.setupUi(self)
        self.setup_callbacks()
        self.active_video_inputs = {}

    @QtCore.pyqtSlot()
    def set_local_stream(self):
        label = QLabel()
        self.gridLayoutConference.setSpacing(1)
        self.gridLayoutConference.addWidget(label, 1, 1)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setScaledContents(True)
        label.setMinimumSize(1, 1)
        label.show()

        worker = VideoWorker("/dev/video0", "local")
        worker.frameReady.connect(self.update_frame)
        worker.packetReady.connect(self.send_packet)
        thread = QtCore.QThread(parent=self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        thread.start()
        self.active_video_inputs["local"] = VideoOutputContainer("local", worker, thread, label)
        self.pushButtonLocalCamera.setEnabled(False)
        self.pushButtonConnect.setEnabled(True)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        camera = self.active_video_inputs.get("local")
        if camera:
            camera.worker.stream.camera.close()

    @QtCore.pyqtSlot(QPixmap, str)
    def update_frame(self, pixmap: QPixmap, name: str):
        self.active_video_inputs[name].label.setPixmap(pixmap)
        self.active_video_inputs[name].label.adjustSize()

    @QtCore.pyqtSlot(TDDFAPredictionContainer)
    def send_packet(self, packet: TDDFAPredictionContainer):
        pass

    @QtCore.pyqtSlot()
    def setup_callbacks(self):
        self.pushButtonLocalCamera.clicked.connect(self.set_local_stream)
