from datetime import datetime


__traffic_border__ = 100


class Telemetry:
    def __init__(self):
        self.prev_time = datetime.utcnow()
        self.frames = 0
        self.total_traffic = 0
        self.current_traffic = 0

    def step_traffic(self, traffic_value):
        self.total_traffic += traffic_value
        self.current_traffic += traffic_value

    def step_frame(self):
        self.frames += 1

    def get_stats(self):
        time = datetime.utcnow()
        timedelta = (time - self.prev_time).total_seconds()
        current = self.current_traffic / timedelta
        total = self.total_traffic
        fps = self.frames / timedelta
        self.current_traffic = 0
        self.frames = 0
        self.prev_time = time
        return current, total, fps

    def stats_ready(self):
        return self.current_traffic > __traffic_border__
