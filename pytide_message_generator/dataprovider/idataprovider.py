from typing import List, Union, Dict, Any

from PyQt6.QtWidgets import QWidget

from pytide_message_generator.dataprovider.message_data import MessageData


class IDataProvider:
    """
    Base Class for all data providers
    """
    def __init__(self):
        pass

    def getName(self) -> str:
        """
        :return: the name of this data provider
        """
        return "UNDEFINED"

    def getUIWidget(self):
        """
        :return: QT UI definition of a widget containing additional configuration options, or none if no additional configuration is needed
        """
        return None

    def loadMessages(self, settings: Union[QWidget, Dict[str, Any]]) -> List[MessageData]:
        if isinstance(settings, QWidget):
            return self.loadMessagesFromWidgetSettings(settings)
        else:
            return self.loadMessagesFromDictSettings(settings)

    def loadMessagesFromWidgetSettings(self, settings: QWidget) -> List[MessageData]:
        return []

    def loadMessagesFromDictSettings(self, settings: Dict) -> List[MessageData]:
        return []