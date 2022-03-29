from abc import ABC, abstractmethod


class VideoStream(ABC):
    @abstractmethod
    def get_current_package(self):
        raise NotImplementedError("NotImplementedError")
