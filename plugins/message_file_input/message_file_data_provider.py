from pathlib import Path
from typing import Union, Dict, Any, List

from PyQt6.QtWidgets import QWidget

from .msgfile_settings_widget import MsgFileSettingsWidget
from pytide_message_generator.dataprovider.idataprovider import IDataProvider
from pytide_message_generator.dataprovider.message_data import MessageData


class MessageFileDataProvider(IDataProvider):
    """
    Base Class for all data providers
    """
    def __init__(self):
        super(MessageFileDataProvider, self).__init__()
        global PLUGIN_DIRECTORY
        PLUGIN_DIRECTORY = str(Path(__file__).resolve().parents[0])

        self.settingsWidget = MsgFileSettingsWidget(PLUGIN_DIRECTORY)

    def getName(self) -> str:
        """
        :return: the name of this data provider
        """
        return "*.msg Files"

    def getUIWidget(self) -> QWidget:
        """
        :return: QT Widget containing additional configuration options, or empty widget if no additional configuration is needed
        """
        return self.settingsWidget

    def loadMessagesFromWidgetSettings(self, settings: QWidget) -> List[MessageData]:
        return []

    def loadMessagesFromDictSettings(self, settings: Dict) -> List[MessageData]:
        return []