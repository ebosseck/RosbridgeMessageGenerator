from typing import List, Any, Dict, Union

from PyQt6.QtWidgets import QWidget

from pytide_message_generator.dataprovider.message_data import MessageData


class IGenerator:
    """
    Base Class for all code generators
    """
    def __init__(self):
        self.enabled: bool = False

    def getLanguage(self) -> str:
        """
        :return: the language the generator generates messages for
        """
        return "UNDEFINED"

    def getUIWidget(self) -> QWidget:
        """
        :return: QT Widget containing additional configuration options, or empty widget if no additional configuration is needed
        """
        return QWidget()

    def generate(self, messages: List[MessageData], settings: Union[QWidget, Dict[str, Any]]):
        if isinstance(settings, QWidget):
            self.generateFromWidgetSettings(messages, settings)
        else:
            self.generateFromDictSettings(messages, settings)

    def generateFromWidgetSettings(self, messages: List[MessageData], settings: QWidget):
        pass

    def generateFromDictSettings(self, messages: List[MessageData], settings: Dict):
        pass