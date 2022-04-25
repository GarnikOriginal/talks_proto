import av


class CameraStream:
    def __init__(self, config):
        self.config = config
        self.name = config["name"]
        self.camera = av.open(self.name, options={"video_size": config["video_size"],
                                                  "framerate": str(config["framerate"])})
        self.steam = self.camera.demux()
        self.context = self.camera.streams.video[0].codec_context
        self.coded_height = self.context.coded_height
        self.coded_width = self.context.coded_width

    def get_current_package(self):
        yield self.steam.__next__()

    def close(self):
        self.camera.close()
