from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QLineEdit, QComboBox, QCheckBox


class PytideSettingsWidget(QWidget):

    def __init__(self, base_path: str, parent: QWidget = None):
        super(PytideSettingsWidget, self).__init__(parent=parent)

        self.base_package_edit: QLineEdit = None
        self.generation_mode_combo: QComboBox = None
        self.flatten_structure_check: QCheckBox = None

        uic.loadUi(base_path + '/resources/gui/settingsWidget.ui', self)
