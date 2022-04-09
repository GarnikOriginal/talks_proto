import cv2
import yaml
import zlib
import pickle
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
from typing import Tuple, List
from modules.TDDFA_V2.FaceBoxes.FaceBoxes import FaceBoxes
from modules.TDDFA_V2.TDDFA import TDDFA
from modules.TDDFA_V2.Sim3DR import rasterize
from modules.TDDFA_V2.utils.tddfa_util import _to_ctype
from modules.TDDFA_V2.utils.uv import bilinear_interpolate


__config_path__ = "configs/tddfa_onnx_config.yml"
__config__ = yaml.load(open(__config_path__), Loader=yaml.SafeLoader)
with open("./core/tri.pkl", "rb") as f:
    __tri__ = pickle.load(f)


class TDDFAPredictionContainer:
    def __init__(self, background: List[np.ndarray], vertices: List[np.ndarray], colors: List[np.ndarray]):
        self.background = background
        self.vertices = vertices
        self.colors = colors

    def encode(self):
        packet = pickle.dumps(self)
        packet = zlib.compress(packet)
        return packet

    def decode(self):
        frames = []
        for i in range(len(self)):
            frame = rasterize(_to_ctype(self.vertices[i].T),
                              __tri__,
                              self.colors[i],
                              bg=self.background[i],
                              height=640,
                              width=480,
                              channel=3)
            frame = QImage(frame, frame.shape[1], frame.shape[0], frame.shape[1] * 3, QImage.Format_RGB888)
            frame = QPixmap.fromImage(frame)
            frames.append(frame)
        return frames

    def __len__(self):
        return len(self.background)


class TDDFAWrapper:
    def __init__(self, background_shape: Tuple[int, int]):
        super(TDDFAWrapper, self).__init__()
        self.tddfa = TDDFA(gpu_mode=False, **__config__)
        self.faceboxes = FaceBoxes()
        self.back_shape = background_shape
        self.background = []
        self.vertices = []
        self.colors = []

    def pop_packet(self):
        packet = TDDFAPredictionContainer(self.background, self.vertices, self.colors)
        self.background = []
        self.vertices = []
        self.colors = []
        return packet

    def forward(self, frame):
        boxes = self.faceboxes(frame)
        background = cv2.resize(frame, self.back_shape, interpolation=cv2.INTER_LINEAR)
        colors, vertices = None, None
        if len(boxes) != 0:
            param_lst, roi_box_lst = self.tddfa(frame, [boxes[0]], crop_policy="box")
            roi_box_lst = [[0, 0, frame.shape[1], frame.shape[0]]]
            vertices = self.tddfa.recon_vers(param_lst, roi_box_lst, DENSE_FLAG=True)[0]
            vertices = _to_ctype(vertices.T)
            colors = bilinear_interpolate(frame, vertices[:, 0], vertices[:, 1]) / 255.
        self.background.append(background)
        self.vertices.append(vertices)
        self.colors.append(colors)
