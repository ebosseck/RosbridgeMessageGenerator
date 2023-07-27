from os import listdir
from os.path import isfile, isdir
from pathlib import Path
from typing import Union, Dict, Any, List

from PyQt6.QtWidgets import QWidget

from .msgfile_settings_widget import MsgFileSettingsWidget
from pytide_message_generator.dataprovider.idataprovider import IDataProvider
from pytide_message_generator.dataprovider.message_data import MessageData
from .ros1msg.ros1parser import Ros1Parser


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

    def loadMessagesFromWidgetSettings(self, settings: MsgFileSettingsWidget) -> List[MessageData]:
        return self.loadMessagesFromDictSettings({
            "path": settings.dir_line_edit.text(),
        })

    def loadMessagesFromDictSettings(self, settings: Dict) -> List[MessageData]:
        if not isdir(settings['path']):
            return []

        print("Loading Messages from Path: '{}'".format(settings['path']))
        fileNames = self.listAllFiles(settings['path'], settings)

        parser = Ros1Parser()

        types = []
        for filename in fileNames:
            types.append(self.extractTypes(filename))

        parser.buildTypeChecks(types)

        messages = []

        for t in types:
            if t[2].endswith('.msg'):
                #try:
                messages.append(parser.parseMessage(*t))
                #except Exception as ex:
                #    print(ex)
            if t[2].endswith('.srv'):
                #try:
                #    print(" ".join(t))
                messages.extend(parser.parseService(*t))
                #except Exception as ex:
                #    print(ex)
        return messages

    def extractTypes(self, filename: str):
        file = filename.split('/')
        if file[-2] != 'msgs' and file[-2] != 'srvs':
            print("Expected Message file to be in folder '[package]/msgs/[name].msg', but found in: {}".format("/".join(file[-3:])))
        else:
            names = file[-1].split('.')
            msg_name = '.'.join(names[:-1])
            pkg_name = file[-3]
            return (pkg_name, msg_name, filename)

    def listAllFiles(self, path, settings: Dict):
        data = []
        for f in listdir(path):
            if isfile(path + "/" + f):
                data.append(path + "/" + f)

            if isdir(path + "/" + f):
                data.extend(self.listAllFiles(path + "/" + f, settings))

        return data

