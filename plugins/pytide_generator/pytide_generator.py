from pathlib import Path
from typing import List, Dict

from PyQt6.QtWidgets import QWidget, QLineEdit

from .pytide_gen.generator import CodeGenerator
from .pytide_settings_widget import PytideSettingsWidget
from pytide_message_generator.dataprovider.message_data import MessageData
from pytide_message_generator.generator.igenerator import IGenerator


class PytideGenerator(IGenerator):
    """
    Base Class for all code generators
    """
    def __init__(self):
        super(PytideGenerator, self).__init__()
        global PLUGIN_DIRECTORY
        PLUGIN_DIRECTORY = str(Path(__file__).resolve().parents[0])

        self.settingsWidget = PytideSettingsWidget(PLUGIN_DIRECTORY)
        self.generator = CodeGenerator(PLUGIN_DIRECTORY)

    def getLanguage(self) -> str:
        """
        :return: the language the generator generates messages for
        """
        return "Python 3"

    def getUIWidget(self) -> QWidget:
        """
        :return: QT Widget containing additional configuration options, or empty widget if no additional configuration is needed
        """
        return self.settingsWidget

    def generateFromWidgetSettings(self, messages: List[MessageData], messageDB: Dict[str, MessageData], path: str, settings: PytideSettingsWidget):
        settings_dict = {}
        settings_dict['base_package'] = settings.base_package_edit.text()
        settings_dict['generation_mode'] = settings.generation_mode_combo.currentIndex()
        settings_dict['flatten_structure'] = settings.base_package_edit.text()

        self.generateFromDictSettings(messages, messageDB, path, settings_dict)

    def generateFromDictSettings(self, messages: List[MessageData], messageDB: Dict[str, MessageData], path: str, settings: Dict):
        ros_gen = CodeGenerator(PLUGIN_DIRECTORY)

        for message in messages:
            ros_gen.generateFile(message, messageDB, settings)

        ros_gen.writeOutFiles(path, settings)