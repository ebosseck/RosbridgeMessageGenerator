from pathlib import Path
from typing import Union, Dict, Any, List

from PyQt6.QtWidgets import QWidget

from pytide_message_generator.dataprovider.field_data import FieldData
from .dummy_settings_widget import DummySettingsWidget
from pytide_message_generator.dataprovider.idataprovider import IDataProvider
from pytide_message_generator.dataprovider.message_data import MessageData


class DummyDataProvider(IDataProvider):
    """
    Base Class for all data providers
    """
    def __init__(self):
        super(DummyDataProvider, self).__init__()
        global PLUGIN_DIRECTORY
        PLUGIN_DIRECTORY = str(Path(__file__).resolve().parents[0])

        self.settingsWidget = DummySettingsWidget(PLUGIN_DIRECTORY)
        self.messages = [
            MessageData(package = ["dummy", "package"], name = "FirstMessage", fields = [
                FieldData(field_type= "string", field_name= "first_string")
            ]),
            MessageData(package= ["dummy", "package"], name="SecondMessage", fields=[
                FieldData(field_type="string", field_name="first_string")
            ]),
            MessageData(package=["another", "package"], name="FirstMessage", fields=[
                FieldData(field_type="string", field_name="first_string")
            ]),
            MessageData(package=["another", "package"], name="SecondMessage", fields=[
                FieldData(field_type="string", field_name="first_string")
            ]),
        ]

    def getName(self) -> str:
        """
        :return: the name of this data provider
        """
        return "DEBUG DATA"

    def getUIWidget(self) -> QWidget:
        """
        :return: QT Widget containing additional configuration options, or empty widget if no additional configuration is needed
        """
        return self.settingsWidget

    def loadMessagesFromWidgetSettings(self, settings: QWidget) -> List[MessageData]:
        return self.messages

    def loadMessagesFromDictSettings(self, settings: Dict) -> List[MessageData]:
        return self.messages