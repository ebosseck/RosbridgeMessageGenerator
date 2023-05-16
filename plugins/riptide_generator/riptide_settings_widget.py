from PyQt6 import uic
from PyQt6.QtWidgets import QWidget


class RiptideSettingsWidget(QWidget):

    def __init__(self, base_path: str, parent: QWidget = None):
        super(RiptideSettingsWidget, self).__init__(parent=parent)
        uic.loadUi(base_path + '/resources/gui/settingsWidget.ui', self)
