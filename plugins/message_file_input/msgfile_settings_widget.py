from PyQt6 import uic
from PyQt6.QtWidgets import QWidget


class MsgFileSettingsWidget(QWidget):

    def __init__(self, base_path: str, parent: QWidget = None):
        super(MsgFileSettingsWidget, self).__init__(parent=parent)
        print("Loading " + base_path + '/resources/gui/settingsWidget.ui')
        uic.loadUi(base_path + '/resources/gui/settingsWidget.ui', self)
