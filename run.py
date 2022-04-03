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
