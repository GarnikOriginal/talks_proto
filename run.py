import sys
import asyncio
from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import QApplication
from asyncqt import QEventLoop
from common.MainForm import MainForm


def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    main_form = MainForm(app, loop)
    main_form.show()
    with loop:
        sys.exit(loop.run_forever())


if __name__ == '__main__':
    main()

    """
    import av
    import cv2
    from time import sleep

    camera = av.open('/dev/video0')
    i = 0
    cv2.namedWindow("1")
    stream = camera.demux()

    for packet in stream:
        sleep(1e-2)
        for frame in packet.decode():
            cv2.imshow("1", frame.to_ndarray(format='bgr24'))
            key = cv2.waitKey(1)
            if key == 27 or i > 100:
                break
            i += 1
            print(f"Frame: {i}")
        if key == 27 or i > 100:
            break
    cv2.destroyAllWindows()
    """
