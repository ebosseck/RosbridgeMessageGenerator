from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QLineEdit, QToolButton

from pytide_message_generator.tools.ui_interaction_tools import setup_folder_select


class WorkspaceInputSettingsWidget(QWidget):

    def __init__(self, base_path: str, parent: QWidget = None):
        super(WorkspaceInputSettingsWidget, self).__init__(parent=parent)

        uic.loadUi(base_path + '/resources/gui/settingsWidget.ui', self)
