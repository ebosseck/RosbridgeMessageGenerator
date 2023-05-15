from typing import List

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

    def loadMessages(self, settings) -> List[MessageData]:
        return []