import av
from .VideoStream import VideoStream


class LocalStream(VideoStream):
    def __init__(self, device_name="/dev/video0"):
        self.name = device_name
        self.camera = av.open(self.name)
        self.steam = self.camera.demux()

    def get_current_package(self):
        yield self.steam.__next__()

    def __del__(self):
        self.camera.close()
