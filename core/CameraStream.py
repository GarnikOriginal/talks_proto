import av
import json


with open('configs/camera.json', "r") as f:
    __config__ = json.load(f)


class CameraStream:
    def __init__(self):
        self.name = __config__["name"]
        self.camera = av.open(self.name, options={"video_size": __config__["video_size"],
                                                  "framerate": __config__["framerate"]})
        self.steam = self.camera.demux()
        self.context = self.camera.streams.video[0].codec_context
        self.coded_height = self.context.coded_height
        self.coded_width = self.context.coded_width

    def get_current_package(self):
        yield self.steam.__next__()

    def __del__(self):
        self.camera.close()
