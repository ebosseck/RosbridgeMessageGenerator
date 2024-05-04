from pathlib import Path
from typing import List, Dict

from PyQt6.QtWidgets import QWidget

from .riptide_gen.generator import CodeGenerator
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
        return "Unity / C#"

    def getUIWidget(self) -> QWidget:
        """
        :return: QT Widget containing additional configuration options, or empty widget if no additional configuration is needed
        """
        return self.settingsWidget

    def generateFromWidgetSettings(self, messages: List[MessageData], messageDB: Dict[str, MessageData], path: str, settings: RiptideSettingsWidget):
        settings_dir = {
            "namespace": settings.namespace_edit.text(),
            "generation_mode": settings.generation_mode_combo.currentIndex(),
            "flatten_structure": settings.flatten_structure_check.isChecked(),
            "partial_class": settings.partial_class_check.isChecked(),
            "common_base": settings.common_base_check.isChecked(),
            "common_base_namespace": settings.base_namespace_edit.text(),
            "common_base_class": settings.base_class_edit.text(),
        }

        return self.generateFromDictSettings(messages, messageDB, path, settings_dir)

    def generateFromDictSettings(self, messages: List[MessageData], messageDB: Dict[str, MessageData], path: str, settings: Dict):
        ros_gen = CodeGenerator(PLUGIN_DIRECTORY)

        for message in messages:
            ros_gen.generateFile(message, messageDB, settings)

        ros_gen.writeOutFiles(path, settings)