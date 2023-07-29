from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

import sys
import traceback

from pytide_message_generator.ui.mainwindow import MainWindow


def dark():
    """
    Sets the UI Colorsheme to Dark
    :return: None
    """
    return QPalette(QColor(53, 53, 53))


def run():
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setStyle('Fusion')
    app.setPalette(dark())

    window.show()
    app.exec()


if __name__ == "__main__":
    run()