from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QLineEdit, QToolButton

from pytide_message_generator.tools.ui_interaction_tools import setup_folder_select


class MsgFileSettingsWidget(QWidget):

    def __init__(self, base_path: str, parent: QWidget = None):
        super(MsgFileSettingsWidget, self).__init__(parent=parent)

        self.dir_line_edit: QLineEdit = None
        self.dir_change_btn: QToolButton = None

        uic.loadUi(base_path + '/resources/gui/settingsWidget.ui', self)

        setup_folder_select(self.dir_change_btn, self.dir_line_edit)