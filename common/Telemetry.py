import json
from datetime import datetime


__traffic_border__ = 100


class Telemetry:
    def __init__(self, write_log):
        self.prev_time = datetime.utcnow()
        self.frames = 0
        self.total_traffic = 0
        self.current_traffic = 0
        self.log = {"time": [], "total": [], "current": [], "per_frame": [], "fps": []}
        self.write_log = write_log
        self.start_time = datetime.utcnow()

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
        per_frame = current / self.frames
        self.current_traffic = 0
        self.frames = 0
        self.prev_time = time
        if self.write_log:
            self.log["time"].append((time - self.start_time).total_seconds())
            self.log["total"].append(total)
            self.log["current"].append(current)
            self.log["per_frame"].append(per_frame)
            self.log["fps"].append(fps)
        return current, per_frame, total, fps

    def stats_ready(self):
        return self.current_traffic > __traffic_border__

    def save_logs(self):
        name = f"{self.start_time.hour}:{self.start_time.minute}.log"
        with open(name, "w") as f:
            json.dump(self.log, f)
