from pathlib import Path
from typing import List, Dict

from PyQt6.QtWidgets import QWidget

from .riptide_settings_widget import RiptideSettingsWidget
from pytide_message_generator.dataprovider.message_data import MessageData
from pytide_message_generator.generator.igenerator import IGenerator


class RiptideGenerator(IGenerator):
    """
    Base Class for all code generators
    """
    def __init__(self):
        super(RiptideGenerator, self).__init__()
        global PLUGIN_DIRECTORY
        PLUGIN_DIRECTORY = str(Path(__file__).resolve().parents[0])

        self.settingsWidget = RiptideSettingsWidget(PLUGIN_DIRECTORY)

    def getLanguage(self) -> str:
        """
        :return: the language the generator generates messages for
        """
        return "C#"

    def getUIWidget(self) -> QWidget:
        """
        :return: QT Widget containing additional configuration options, or empty widget if no additional configuration is needed
        """
        return self.settingsWidget

    def generateFromWidgetSettings(self, messages: List[MessageData], messageDB: Dict[str, MessageData], path: str, settings: QWidget):
        pass

    def generateFromDictSettings(self, messages: List[MessageData], messageDB: Dict[str, MessageData], path: str, settings: Dict):
        pass