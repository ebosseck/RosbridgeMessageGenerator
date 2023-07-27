from os import makedirs
from typing import Dict, List, Tuple

from pytide_message_generator.dataprovider.field_data import FieldData
from pytide_message_generator.dataprovider.message_data import MessageData

from os.path import isfile, isdir, exists

from pytide_message_generator.io.filewriter import writeFile


class Ros1Gen:

    def __init__(self):
        self.messages_names: List[str] = []
        self.generated_messages: Dict[str, Tuple[str, MessageData]] = {}

        self.generated_services: List[str] = []

    def generateFile(self, message: MessageData, messageDB: Dict[str, MessageData], settings: Dict):
        if message.isService:
            self.generateService(message, messageDB, settings)
        else:
            self.generateMessage(message, messageDB, settings)

    def generateService(self, message: MessageData, messageDB: Dict[str, MessageData], settings: Dict):
        if message.srv_name in self.generated_services:
            return
        service_msgs = [message, *message.srv_siblings]

        def getID(message: MessageData):
            return message.srv_index

        service_msgs.sort(key=getID)

        src = []

        for msg in service_msgs:
            fields = []
            for field in msg.fields:
                fields.append(self.generateField(field, messageDB, settings))
            src.append('\n'.join(fields))

        self.messages_names.append(message.getID())
        self.generated_messages[message.getID()] = ("\n---\n".join(src), message)
        self.generated_services.append(message.srv_name)

    def generateMessage(self, message: MessageData, messageDB: Dict[str, MessageData], settings: Dict):
        fields = []

        for field in message.fields:
            fields.append(self.generateField(field, messageDB, settings))

        self.messages_names.append(message.getID())
        self.generated_messages[message.getID()] = ("\n".join(fields), message)


    def generateField(self, field: FieldData, messageDB: Dict[str, MessageData], settings: Dict) -> str:
        field_value = []

        field_value.append(field.field_type)

        if field.is_array:
            field_value.append('[')
            if field.array_fixed_length >= 0:
                field_value.append(str(field.array_fixed_length))
            field_value.append(']')

        field_value.append(' ')
        field_value.append(field.field_name)

        if field.constant_value is not None:
            field_value.append(' = ')
            field_value.append(str(field.constant_value))

        return ''.join(field_value)

    def writeOutFiles(self, base_path: str):
        for msgID in self.generated_messages:
            source, message = self.generated_messages[msgID]
            messagePath = base_path + "/msg_files"
            for package in message.package:
                messagePath += '/' + package


            if message.isService:
                messagePath += '/srvs'
                if not exists(messagePath):
                    makedirs(messagePath)
                writeFile(messagePath + '/' + message.srv_name + '.srv', source)
            else:
                messagePath += '/msgs'
                if not exists(messagePath):
                    makedirs(messagePath)
                writeFile(messagePath + '/' + message.name + '.msg', source)


    def clear(self):
        self.messages_names.clear()
        self.generated_messages.clear()