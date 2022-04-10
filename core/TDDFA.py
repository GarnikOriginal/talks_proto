import av
import cv2
import yaml
import zlib
import pickle
import numpy as np
from fractions import Fraction
from PyQt5.QtGui import QImage, QPixmap
from typing import Tuple, Dict
from modules.TDDFA_V2.FaceBoxes.FaceBoxes import FaceBoxes
from modules.TDDFA_V2.TDDFA import TDDFA
from modules.TDDFA_V2.Sim3DR import rasterize
from modules.TDDFA_V2.utils.tddfa_util import _to_ctype
from modules.TDDFA_V2.utils.uv import bilinear_interpolate


__yuv420p__ = av.video.format.VideoFormat('yuv420p')
__bgr24__ = av.video.format.VideoFormat('bgr24')
__config_path__ = "configs/tddfa_onnx_config.yml"
__config__ = yaml.load(open(__config_path__), Loader=yaml.SafeLoader)
with open("./core/tri.pkl", "rb") as f:
    __tri__ = pickle.load(f)


class TDDFAPredictionContainer:
    def __init__(self, background: Dict[int, np.ndarray], vertices: Dict[int, np.ndarray], colors: Dict[int, np.ndarray]):
        self.background = background
        self.vertices = vertices
        self.colors = colors

    def encode(self, context):
        for key in self.background.keys():
            frame = self.background[key]
            frame = av.VideoFrame.from_ndarray(frame, format="bgr24")
            frame = frame.reformat(width=480, height=640, format=__yuv420p__)
            self.background[key] = self.packet_to_bytes(context.encode(frame)[0])
        packet = pickle.dumps(self)
        packet = zlib.compress(packet)
        return packet

    def decode(self, context):
        frames = []
        for key in self.background.keys():
            bg = self.packet_from_bytes(self.background[key])
            bg = context.decode(bg)[0]
            bg = bg.reformat(format=__bgr24__).to_ndarray()
            bg = cv2.blur(cv2.resize(bg, (context.height, context.width), cv2.INTER_NEAREST), (3, 3))
            if key in self.vertices.keys():
                frame = rasterize(self.vertices[key],
                                  __tri__,
                                  self.colors[key],
                                  bg=bg,
                                  height=context.height,
                                  width=context.width,
                                  channel=3)
            else:
                frame = bg
            frame = QImage(frame, frame.shape[1], frame.shape[0], frame.shape[1] * 3, QImage.Format_RGB888)
            frame = QPixmap.fromImage(frame)
            frames.append(frame)
        return frames

    def packet_to_bytes(self, packet):
        encoded_packet = packet.dts.to_bytes(4, byteorder='big')
        encoded_packet += packet.pts.to_bytes(4, byteorder='big')
        encoded_packet += packet.time_base.denominator.to_bytes(4, byteorder='big')
        encoded_packet += packet.time_base.numerator.to_bytes(4, byteorder='big')
        encoded_packet += packet.to_bytes()
        return encoded_packet

    def packet_from_bytes(self, packet):
        pack = av.Packet(packet[16:])
        pack.dts = int.from_bytes(packet[0:4], byteorder="big")
        pack.pts = int.from_bytes(packet[4:8], byteorder="big")
        denominator = int.from_bytes(packet[8:12], byteorder="big")
        numerator = int.from_bytes(packet[12:16], byteorder="big")
        pack.time_base = Fraction(numerator, denominator)
        return pack

    def __len__(self):
        return len(self.background)


class TDDFAWrapper:
    def __init__(self, background_shape: Tuple[int, int]):
        super(TDDFAWrapper, self).__init__()
        self.tddfa = TDDFA(gpu_mode=False, **__config__)
        self.faceboxes = FaceBoxes()
        self.back_shape = background_shape
        self.background = {}
        self.vertices = {}
        self.colors = {}
        self.frame_num = 0
        self.first_frame = True

    def pop_packet(self):
        packet = TDDFAPredictionContainer(self.background, self.vertices, self.colors)
        self.background = {}
        self.vertices = {}
        self.colors = {}
        self.frame_num = 0
        return packet

    def forward(self, frame):
        boxes = self.faceboxes(frame)
        background = cv2.resize(frame, self.back_shape, interpolation=cv2.INTER_LINEAR)
        if len(boxes) != 0:
            param_lst, roi_box_lst = self.tddfa(frame, [boxes[0]], crop_policy="box")
            vertices = self.tddfa.recon_vers(param_lst, roi_box_lst, DENSE_FLAG=True)[0]
            vertices = _to_ctype(vertices.T)
            colors = bilinear_interpolate(frame, vertices[:, 0], vertices[:, 1]) / 255.
            self.vertices[self.frame_num] = vertices
            self.colors[self.frame_num] = colors
        self.background[self.frame_num] = background
        self.first_frame = False
