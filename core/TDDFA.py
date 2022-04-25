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
from modules.TDDFA_V2.utils.uv import bilinear_interpolate, uv_tex, g_uv_coords, process_uv


__yuv420p__ = av.video.format.VideoFormat('yuv420p')
__bgr24__ = av.video.format.VideoFormat('bgr24')
__uv_text_h__ = 256
__uv_text_w__ = 256
__config_path__ = "configs/tddfa_onnx_config.yml"
__config__ = yaml.load(open(__config_path__), Loader=yaml.SafeLoader)
__uv_cords__ = _to_ctype(process_uv(g_uv_coords.copy(), uv_h=__uv_text_h__, uv_w=__uv_text_w__))
with open("./core/tri.pkl", "rb") as f:
    __tri__ = pickle.load(f)
__tddfa__ = TDDFA(gpu_mode=False, **__config__)


class TDDFAPredictionContainer:
    def __init__(self,
                 background: Dict[int, np.ndarray],
                 deep_features: Dict[int, np.ndarray],
                 roi_boxes: Dict[int, np.ndarray],
                 uv_textures: Dict[int, np.ndarray]):
        self.background = background
        self.deep_features = deep_features
        self.roi_boxes = roi_boxes
        self.uv_textures = uv_textures

    def encode(self, bg_context, uv_context):
        for key in self.background.keys():
            frame = av.VideoFrame.from_ndarray(self.background[key], format="bgr24")
            frame = frame.reformat(format=__yuv420p__)
            self.background[key] = self.packet_to_bytes(bg_context.encode(frame)[0])
            if key in self.uv_textures.keys():
                uv_text = av.VideoFrame.from_ndarray(self.uv_textures[key], format="bgr24")
                uv_text = uv_text.reformat(format=__yuv420p__)
                self.uv_textures[key] = self.packet_to_bytes(uv_context.encode(uv_text)[0])
        packet = pickle.dumps(self)
        packet = zlib.compress(packet)
        return packet

    def decode(self, bg_context, uv_context, result_shape):
        frames = []
        for key in self.background.keys():
            bg = self.decode_packet(self.background[key], bg_context)
            bg = cv2.resize(bg, result_shape, cv2.INTER_LINEAR)
            bg = cv2.blur(bg, (3, 3))
            if key in self.uv_textures.keys():
                uv_text = self.decode_packet(self.uv_textures[key], uv_context)
                colors = bilinear_interpolate(uv_text, __uv_cords__[:, 0], __uv_cords__[:, 1]) / 255.
                ver = __tddfa__.recon_vers([self.deep_features[key]], [self.roi_boxes[key]], DENSE_FLAG=True)[0]
                ver = _to_ctype(ver.T)
                frame = rasterize(ver, __tri__, colors, bg=bg)
            else:
                frame = bg
            frame = QImage(frame, frame.shape[1], frame.shape[0], frame.shape[1] * 3, QImage.Format_RGB888)
            frame = QPixmap.fromImage(frame)
            frames.append(frame)
        return frames

    def decode_packet(self, frame, context):
        frame = self.packet_from_bytes(frame)
        frame = context.decode(frame)[0]
        return frame.reformat(format=__bgr24__).to_ndarray()

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
        self.deep_features = {}
        self.roi_boxes = {}
        self.uv_textures = {}
        self.frame_num = 0

    def pop_packet(self):
        packet = TDDFAPredictionContainer(self.background, self.deep_features, self.roi_boxes, self.uv_textures)
        self.background = {}
        self.deep_features = {}
        self.roi_boxes = {}
        self.uv_textures = {}
        self.frame_num = 0
        return packet

    def forward(self, frame):
        boxes = self.faceboxes(frame)
        background = cv2.resize(frame, self.back_shape, interpolation=cv2.INTER_LINEAR)
        if len(boxes) != 0:
            param_lst, roi_box_lst = self.tddfa(frame, [boxes[0]], crop_policy="box")
            vertices = self.tddfa.recon_vers(param_lst, roi_box_lst, DENSE_FLAG=True)[0]
            uv_texture = uv_tex(frame, [vertices], self.tddfa.tri, uv_h=__uv_text_h__, uv_w=__uv_text_w__)
            self.deep_features[self.frame_num] = param_lst[0]
            self.roi_boxes[self.frame_num] = roi_box_lst[0]
            self.uv_textures[self.frame_num] = uv_texture
        self.background[self.frame_num] = background
