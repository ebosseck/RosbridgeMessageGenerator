from datetime import datetime
from os import makedirs
from os.path import exists
from string import Template
from typing import List, Dict, Tuple

from pytide_message_generator.dataprovider.message_data import MessageData
from pytide_message_generator.io.filewriter import readFile, writeFile

PRIMITIVE_TYPE_MAP = {
    "bool": "bool",
    "int8": "int",
    "uint8": "int",
    "int16": "int",
    "uint16": "int",
    "int32": "int",
    "uint32": "int",
    "int64": "int",
    "uint64": "int",
    "float32": "float",
    "float64": "float",
    "string": "str",
    "time": "Tuple[int, int]",
    "duration": "Tuple[int, int]"
}

PRIMITIVE_DEFAULT_VALUE_MAP = {
    "bool": "False",
    "int8": "0",
    "uint8": "0",
    "int16": "0",
    "uint16": "0",
    "int32": "0",
    "uint32": "0",
    "int64": "0",
    "uint64": "0",
    "float32": "0",
    "float64": "0",
    "string": "''",
    "time": "(0, 0)",
    "duration": "(0, 0)"
}

PRIMITIVE_SERIALISATION_MAP = {
    "bool": "putBool",
    "int8": "putInt8",
    "uint8": "putUInt8",
    "int16": "putInt16",
    "uint16": "putUInt16",
    "int32": "putInt32",
    "uint32": "putUInt32",
    "int64": "putInt64",
    "uint64": "putUInt64",
    "float32": "putFloat",
    "float64": "putDouble",
    "string": "putString",
}

PRIMITIVE_DESERIALISATION_MAP = {
    "bool": "getBool",
    "int8": "getInt8",
    "uint8": "getUInt8",
    "int16": "getInt16",
    "uint16": "getUInt16",
    "int32": "getInt32",
    "uint32": "getUInt32",
    "int64": "getInt64",
    "uint64": "getUInt64",
    "float32": "getFloat",
    "float64": "getDouble",
    "string": "getString",
}

class CodeGenerator:

    def __init__(self, plugin_basepath):

        self.messages_names: List[str] = []
        self.generated_messages: Dict[str, Tuple[str, MessageData]] = {}

        self.dependencyTemplate: Template = Template(readFile(plugin_basepath + '/resources/src/dependency.template'))
        self.constantTemplate: Template = Template(readFile(plugin_basepath + '/resources/src/constant.template'))
        self.constructorTemplate: Template = Template(readFile(plugin_basepath + '/resources/src/constructor.template'))
        self.accessorTemplate: Template = Template(readFile(plugin_basepath + '/resources/src/accessor.template'))

        self.messageTemplate: Template = Template(readFile(plugin_basepath + '/resources/src/message.template'))

    def generateFile(self, message: MessageData, messageDB: Dict[str, MessageData], settings: Dict):
        if message.getID() in self.messages_names:
            return
        self.messages_names.append(message.getID())

        variables = {
            "timestamp": datetime.now().strftime("%d %b %Y, %H:%M:%S"),
            "dependencies": self.generateDependencies(message, messageDB, settings),
            "constants": self.generateConstants(message, messageDB, settings),
            "class_name": self.determineClassName(message, settings),
            "superclass": settings['super_class_name'] if settings['common_super_class'] else '',
            "constructor": self.generateConstructor(message, messageDB, settings),
            "accessors": self.generateAccessors(message, messageDB, settings),
            "message_serializer": self.generateSerializers(message, messageDB, settings),
            "message_deserializer": self.generateDeserializers(message, messageDB, settings),
        }

        self.generated_messages[message.getID()] = (self.messageTemplate.substitute(variables), message)

    def determineClassName(self, message: MessageData, settings: Dict) -> str:
        return message.name

    def determineAlias(self, message: MessageData, settings: Dict) -> str:
        return message.name

    def determinePackageName(self, message: MessageData, settings: Dict):
        base_package = []
        if settings['base_package'] is not None and settings['base_package'] != '':
            base_package = [settings['base_package']]

        return '.'.join([*base_package, *message.package, message.name.lower()])

    def getMessageFromType(self, ownMessage: MessageData, type: str, messageDB: Dict[str, MessageData]) -> MessageData:
        if type in messageDB:
            return messageDB[type]
        else:
            localType = "/".join([*ownMessage.package, type])
            if localType in messageDB:
                return messageDB[localType]
            else:
                print("Missing Dependency for Type: {}".format(type))
                return None

    def generateDependencies(self, message: MessageData, messageDB: Dict[str, MessageData], settings: Dict) -> str:
        types = []
        for field in message.fields:
            types.append(field.field_type)

        types = list(set(types))

        imports = []
        didImportTuple = False

        for type in types:
            if type in PRIMITIVE_TYPE_MAP:
                if not didImportTuple and type in ["time", "duration"]:
                    didImportTuple = True
                    imports.append("from typing import Tuple, List")
            else:
                dependentMessage = self.getMessageFromType(message, type, messageDB)
                if dependentMessage is None:
                    imports.append("# MISSING TYPE: {}".format(type))
                    continue
                self.generateFile(dependentMessage, messageDB, settings)

                imports.append(self.dependencyTemplate.substitute({
                    "package": self.determinePackageName(dependentMessage, settings),
                    "class": self.determineClassName(dependentMessage, settings)
                }))

        if not didImportTuple:
            imports.insert(0, "from typing import List")

        if settings['common_super_class']:
            imports.append("from {} import {}".format(settings['super_class_package'], settings['super_class_name']))

        return '\n'.join(imports)

    def generateConstants(self, message: MessageData, messageDB: Dict[str, MessageData], settings: Dict) -> str:
        constants = []
        for field in message.fields:
            if field.constant_value is not None:
                constants.append(self.constantTemplate.substitute({
                    "name": field.field_name,
                    "type": PRIMITIVE_TYPE_MAP[field.field_type],
                    "value": str(field.constant_value) if not isinstance(field.constant_value, str) else
                        '"{}"'.format(field.constant_value),
                }))

        return '\n'.join(constants)

    def generateConstructor(self, message: MessageData, messageDB: Dict[str, MessageData], settings: Dict) -> str:
        args = ['self']

        content = []
        for field in message.fields:
            if field.constant_value is not None:
                continue
            if field.is_array:
                #TODO: Avoid mutable args
                if field.field_type in PRIMITIVE_TYPE_MAP:
                    args.append("{}: List[{}] = []".format(field.field_name, PRIMITIVE_TYPE_MAP[field.field_type]))

                    content.append(
                        "self.{}: List[{}] = {}".format(field.field_name, PRIMITIVE_TYPE_MAP[field.field_type],
                                                        field.field_name))
                else:
                    dependentMessage = self.getMessageFromType(message, field.field_type, messageDB)
                    type = self.determineAlias(dependentMessage, settings)

                    args.append("{}: List[{}] = []".format(field.field_name, type))

                    content.append("self.{}: List[{}] = {}".format(field.field_name, type,
                                                                   field.field_name))

            else:
                if field.field_type in PRIMITIVE_TYPE_MAP:
                    args.append("{}: {} = {}".format(field.field_name, PRIMITIVE_TYPE_MAP[field.field_type],
                                                     PRIMITIVE_DEFAULT_VALUE_MAP[field.field_type]))

                    content.append("self.{}: {} = {}".format(field.field_name, PRIMITIVE_TYPE_MAP[field.field_type],
                                                             field.field_name))
                else:
                    dependentMessage = self.getMessageFromType(message, field.field_type, messageDB)
                    type = self.determineAlias(dependentMessage, settings)

                    args.append("{}: {} = {}()".format(field.field_name, type, type))

                    content.append("self.{}: {} = {}".format(field.field_name, type,
                                                             field.field_name))

        variables = {
            "args": ", ".join(args),
            "classname": self.determineClassName(message, settings),
            "superargs": "",
            "content": "\n        ".join(content),
            "msgID": message.getID()
        }

        return self.constructorTemplate.substitute(variables)

    def generateAccessors(self, message: MessageData, messageDB: Dict[str, MessageData], settings: Dict) -> str:
        accessors = []

        for field in message.fields:
            if field.constant_value is not None:
                continue
            vars = {
                "name": "".join([field.field_name[0].upper(), field.field_name[1:]]),
                "variable": field.field_name
            }

            if field.is_array:
                if field.field_type in PRIMITIVE_TYPE_MAP:
                    vars["type"] = "List[{}]".format(PRIMITIVE_TYPE_MAP[field.field_type])
                else:
                    dependentMessage = self.getMessageFromType(message, field.field_type, messageDB)
                    type = self.determineAlias(dependentMessage, settings)
                    vars["type"] = "List[{}]".format(type)
            else:
                if field.field_type in PRIMITIVE_TYPE_MAP:
                    vars["type"] = "{}".format(PRIMITIVE_TYPE_MAP[field.field_type])
                else:
                    dependentMessage = self.getMessageFromType(message, field.field_type, messageDB)
                    type = self.determineAlias(dependentMessage, settings)
                    vars["type"] = "{}".format(type)
            accessors.append(self.accessorTemplate.substitute(vars))

        return '\n'.join(accessors)

    def generateSerializers(self, message: MessageData, messageDB: Dict[str, MessageData], settings: Dict) -> str:
        if len(message.fields) < 1:
            return "pass"

        serializers = []
        for field in message.fields:
            if field.constant_value is not None:
                continue
            if field.is_array:
                if field.array_fixed_length < 0:
                    # dynamic length array
                    if field.field_type in PRIMITIVE_SERIALISATION_MAP:
                        serializers.append("message.{}Array(self.{})".format(PRIMITIVE_SERIALISATION_MAP[field.field_type],
                                                                        field.field_name))
                    elif field.field_type == 'time':
                        serializers.append("message.putVarULong(len(self.{}))".format(field.field_name))

                        serializers.append("for i in range(len(self.{})):".format(field.field_name))
                        serializers.append("    message.putUInt32(self.{}[i][0])".format(field.field_name))
                        serializers.append("    message.putUInt32(self.{}[i][1])".format(field.field_name))
                    elif field.field_type == 'duration':
                        serializers.append("message.putVarULong(len(self.{}))".format(field.field_name))

                        serializers.append("for i in range(len(self.{})):".format(field.field_name))
                        serializers.append("    message.putInt32(self.{}[i][0])".format(field.field_name))
                        serializers.append("    message.putInt32(self.{}[i][1])".format(field.field_name))
                    else:
                        serializers.append("message.putVarULong(len(self.{}))".format(field.field_name))
                        serializers.append("for i in range(len(self.{})):".format(field.field_name))
                        serializers.append("    self.{}[i].serializeToMessage(message)".format(field.field_name))
                else:
                    #fixed size array
                    if field.field_type in PRIMITIVE_SERIALISATION_MAP:
                        serializers.append(
                            "message.{}Array(self.{}, includeLength=False)".format(PRIMITIVE_SERIALISATION_MAP[field.field_type],
                                                              field.field_name))
                    elif field.field_type == 'time':
                        serializers.append("for i in range({}):".format(field.array_fixed_length))
                        serializers.append("    message.putUInt32(self.{}[i][0])".format(field.field_name))
                        serializers.append("    message.putUInt32(self.{}[i][1])".format(field.field_name))
                    elif field.field_type == 'duration':
                        serializers.append("for i in range({}):".format(field.array_fixed_length))
                        serializers.append("    message.putInt32(self.{}[i][0])".format(field.field_name))
                        serializers.append("    message.putInt32(self.{}[i][1])".format(field.field_name))
                    else:
                        serializers.append("for i in range({}):".format(field.array_fixed_length))
                        serializers.append("    self.{}[i].serializeToMessage(message)".format(field.field_name))
            else:
                if field.field_type in PRIMITIVE_SERIALISATION_MAP:
                    serializers.append("message.{}(self.{})".format(PRIMITIVE_SERIALISATION_MAP[field.field_type],
                                                                    field.field_name))
                elif field.field_type == 'time':
                    serializers.append("message.putUInt32(self.{}[0])".format(field.field_name))
                    serializers.append("message.putUInt32(self.{}[1])".format(field.field_name))
                elif field.field_type == 'duration':
                    serializers.append("message.putInt32(self.{}[0])".format(field.field_name))
                    serializers.append("message.putInt32(self.{}[1])".format(field.field_name))
                else:
                    serializers.append("self.{}.serializeToMessage(message)".format(field.field_name))

        return "\n        ".join(serializers)

    def generateDeserializers(self, message: MessageData, messageDB: Dict[str, MessageData], settings: Dict) -> str:
        if len(message.fields) < 1:
            return "pass"

        deserializers = []
        for field in message.fields:
            if field.constant_value is not None:
                continue
            if field.is_array:
                if field.array_fixed_length < 0:
                    # dynamic length array
                    if field.field_type in PRIMITIVE_DESERIALISATION_MAP:
                        deserializers.append("self.{} = message.{}Array()".format(field.field_name,
                                                                                  PRIMITIVE_DESERIALISATION_MAP[field.field_type]))
                    elif field.field_type == 'time':
                        deserializers.append("length = message.getVarULong()")

                        deserializers.append("self.{} = []".format(field.field_name))
                        deserializers.append("for i in range(length):")
                        deserializers.append("    self.{}.append((message.getUInt(), message.getUInt()))".format(field.field_name))

                    elif field.field_type == 'duration':
                        deserializers.append("length = message.getVarULong()")

                        deserializers.append("self.{} = []".format(field.field_name))
                        deserializers.append("for i in range(length):")
                        deserializers.append("    self.{}.append((message.getInt(), message.getInt()))".format(field.field_name))
                    else:
                        deserializers.append("length = message.getVarULong()")

                        deserializers.append("self.{} = []".format(field.field_name))
                        deserializers.append("for i in range(length):")

                        dependentMessage = self.getMessageFromType(message, field.field_type, messageDB)
                        type = self.determineAlias(dependentMessage, settings)

                        deserializers.append("    value: {} = {}()".format(type, type))
                        deserializers.append("    value.deserializeFromMessage(message)")
                        deserializers.append("    self.{}.append(value)".format(field.field_name))
                else:
                    #fixed size array
                    if field.field_type in PRIMITIVE_DESERIALISATION_MAP:
                        deserializers.append("self.{} = message.{}Array(length={})".format(field.field_name,
                                                                                  PRIMITIVE_DESERIALISATION_MAP[
                                                                                      field.field_type],
                                                                                           field.array_fixed_length))
                    elif field.field_type == 'time':

                        deserializers.append("self.{} = []".format(field.field_name))
                        deserializers.append("for i in range({}):".format(field.array_fixed_length))
                        deserializers.append(
                            "    self.{}.append((message.getUInt(), message.getUInt()))".format(field.field_name))

                    elif field.field_type == 'duration':
                        deserializers.append("self.{} = []".format(field.field_name))
                        deserializers.append("for i in range({}):".format(field.array_fixed_length))
                        deserializers.append(
                            "    self.{}.append((message.getInt(), message.getInt()))".format(field.field_name))
                    else:

                        deserializers.append("self.{} = []".format(field.field_name))
                        deserializers.append("for i in range({}):".format(field.array_fixed_length))

                        dependentMessage = self.getMessageFromType(message, field.field_type, messageDB)
                        type = self.determineAlias(dependentMessage, settings)

                        deserializers.append("    value: {} = {}()".format(type, type))
                        deserializers.append("    value.deserializeFromMessage(message)")
                        deserializers.append("    self.{}.append(value)".format(field.field_name))
            else:
                if field.field_type in PRIMITIVE_DESERIALISATION_MAP:
                    deserializers.append("self.{} = message.{}()".format(field.field_name, PRIMITIVE_DESERIALISATION_MAP[field.field_type]))
                elif field.field_type == 'time':
                    deserializers.append("self.{} = (message.getUInt32(), message.getUInt32())".format(field.field_name))
                elif field.field_type == 'duration':
                    deserializers.append(
                        "self.{} = (message.getInt32(), message.getInt32())".format(field.field_name))
                else:
                    dependentMessage = self.getMessageFromType(message, field.field_type, messageDB)
                    type = self.determineAlias(dependentMessage, settings)
                    deserializers.append("self.{} = {}()".format(field.field_name, type))
                    deserializers.append("self.{}.deserializeFromMessage(message)".format(field.field_name))

        return "\n        ".join(deserializers)

    def checkPackage(self, path):
        if not exists(path):
            makedirs(path)
            writeFile("{}/__init__.py".format(path), "")

    def writeOutFiles(self, base_path: str, settings: Dict):
        for msgID in self.generated_messages:
            source, message = self.generated_messages[msgID]

            messagePath = base_path + "/pytide"

            if not exists(messagePath):
                makedirs(messagePath)

            basePackage = settings['base_package'].split('.')

            for package in basePackage:
                messagePath += '/' + package
                self.checkPackage(messagePath)

            for package in message.package:
                messagePath += '/' + package
                self.checkPackage(messagePath)

            writeFile("{}/{}.py".format(messagePath, message.name.lower()), source)

    def clear(self):
        self.messages_names.clear()
        self.generated_messages.clear()
