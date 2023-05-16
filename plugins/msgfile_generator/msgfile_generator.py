from pathlib import Path
from typing import List, Dict

from PyQt6.QtWidgets import QWidget

from .msgfile_settings_widget import MsgFileSettingsWidget
from pytide_message_generator.dataprovider.message_data import MessageData
from pytide_message_generator.generator.igenerator import IGenerator


class MsgFileGenerator(IGenerator):
    """
    Base Class for all code generators
    """
    def __init__(self):
        super(MsgFileGenerator, self).__init__()
        global PLUGIN_DIRECTORY
        PLUGIN_DIRECTORY = str(Path(__file__).resolve().parents[0])

    def getLanguage(self) -> str:
        """
        :return: the language the generator generates messages for
        """
        return "*.msg Files"

    def getUIWidget(self) -> QWidget:
        """
        :return: QT Widget containing additional configuration options, or empty widget if no additional configuration is needed
        """
        return MsgFileSettingsWidget(PLUGIN_DIRECTORY)

    def generateFromWidgetSettings(self, messages: List[MessageData], settings: QWidget):
        pass

    def generateFromDictSettings(self, messages: List[MessageData], settings: Dict):
        pass