from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QLineEdit, QComboBox, QCheckBox


class RiptideSettingsWidget(QWidget):

    def __init__(self, base_path: str, parent: QWidget = None):
        super(RiptideSettingsWidget, self).__init__(parent=parent)

        self.namespace_edit: QLineEdit = None
        self.generation_mode_combo: QComboBox = None
        self.flatten_structure_check: QCheckBox = None
        self.partial_class_check: QCheckBox = None
        self.common_base_check: QCheckBox = None

        self.base_namespace_edit: QLineEdit = None
        self.base_class_edit: QLineEdit = None

        uic.loadUi(base_path + '/resources/gui/settingsWidget.ui', self)
