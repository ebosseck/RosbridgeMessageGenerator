from datetime import datetime
from os import makedirs
from os.path import exists
from string import Template
from typing import List, Dict, Tuple

from pytide_message_generator.dataprovider.message_data import MessageData
from pytide_message_generator.io.filewriter import readFile, writeFile

PRIMITIVE_TYPE_MAP = {
    "bool": "bool",
    "int8": "sbyte",
    "uint8": "byte",
    "int16": "short",
    "uint16": "ushort",
    "int32": "int",
    "uint32": "uint",
    "int64": "long",
    "uint64": "ulong",
    "float32": "float",
    "float64": "double",
    "string": "string",
    "time": "uint[]",
    "duration": "int[]"
}

PRIMITIVE_SUFFIX_MAP = {
    "bool": "",
    "int8": "",
    "uint8": "",
    "int16": "",
    "uint16": "",
    "int32": "",
    "uint32": "",
    "int64": "",
    "uint64": "",
    "float32": "f",
    "float64": "",
    "string": "",
    "time": "",
    "duration": ""
}


PRIMITIVE_DEFAULT_VALUE_MAP = {
    "bool": "false",
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
    "string": '""',
    "time": "null",
    "duration": "null"
}

PRIMITIVE_SERIALISATION_MAP = {
    "bool": "AddBool",
    "int8": "AddSByte",
    "uint8": "AddByte",
    "int16": "AddShort",
    "uint16": "AddUShort",
    "int32": "AddInt",
    "uint32": "AddUInt",
    "int64": "AddLong",
    "uint64": "AddULong",
    "float32": "AddFloat",
    "float64": "AddDouble",
    "string": "AddString",
}

PRIMITIVE_DESERIALISATION_MAP = {
    "bool": "GetBool",
    "int8": "GetSByte",
    "uint8": "GetByte",
    "int16": "GetShort",
    "uint16": "GetUShort",
    "int32": "GetInt",
    "uint32": "GetUInt",
    "int64": "GetLong",
    "uint64": "GetULong",
    "float32": "GetFloat",
    "float64": "GetDouble",
    "string": "GetString",
}

CSHARP_KEYWORDS = ["abstract", "as", "base", "bool", "break", "byte", "case", "catch", "char", "checked", "class",
                   "const", "continue", "decimal", "default", "delegate", "do", "double", "else", "enum", "event",
                   "explicit", "extern", "false", "finally", "fixed", "float", "for", "foreach", "goto", "if",
                   "implicit", "in", "int", "interface", "internal", "is", "lock", "long", "namespace", "new", "null",
                   "object", "operator", "out", "override", "params", "private", "protected", "public", "readonly",
                   "ref", "return", "sbyte", "sealed", "short", "sizeof", "stackalloc", "static", "string", "struct",
                   "switch", "this", "throw", "true", "try", "typeof", "uint", "ulong", "unchecked", "unsafe", "ushort",
                   "using", "virtual", "void", "volatile", "while"]

class CodeGenerator:

    def __init__(self, plugin_basepath):

        self.messages_names: List[str] = []
        self.generated_messages: Dict[str, Tuple[str, MessageData]] = {}

        self.dependencyTemplate: Template = Template(readFile(plugin_basepath + '/resources/src/dependency.template'))
        self.constantTemplate: Template = Template(readFile(plugin_basepath + '/resources/src/constant.template'))
        self.fieldTemplate: Template = Template(readFile(plugin_basepath + '/resources/src/field.template'))
        self.constructorTemplate: Template = Template(readFile(plugin_basepath + '/resources/src/constructor.template'))

        self.messageTemplate: Template = Template(readFile(plugin_basepath + '/resources/src/message.template'))

    def generateFile(self, message: MessageData, messageDB: Dict[str, MessageData], settings: Dict):
        if message.getID() in self.messages_names:
            return
        self.messages_names.append(message.getID())

        variables = {
            "timestamp": datetime.now().strftime("%d %b %Y, %H:%M:%S"),
            "dependencies": self.generateDependencies(message, messageDB, settings),
            "namespace": self.determineNamespace(message, settings),
            "class_keywords": " partial" if settings['partial_class'] else "",
            "class_name": self.determineClassName(message, settings),
            "superclass": ": {}".format(settings['common_base_class']) if settings['common_base'] else '',
            "constants": self.generateConstants(message, messageDB, settings),
            "fields": self.generateFields(message, messageDB, settings),
            "constructor": self.generateConstructor(message, messageDB, settings),
            "message_serializer": self.generateSerializers(message, messageDB, settings),
            "message_deserializer": self.generateDeserializers(message, messageDB, settings),
        }

        self.generated_messages[message.getID()] = (self.messageTemplate.substitute(variables), message)

    def sanitizeFieldName(self, name: str):
        if name in CSHARP_KEYWORDS:
            return "_{}".format(name)
        return name

    def determineClassName(self, message: MessageData, settings: Dict) -> str:
        return "{}Message".format(message.name)

    def determineAlias(self, message: MessageData, settings: Dict) -> str:
        return "{}Message".format(message.name)

    def determineNamespace(self, message: MessageData, settings: Dict):
        namespace = []
        if settings['namespace'] is not None and settings['namespace'] != '':
            namespace = [settings['namespace']]

        return '.'.join([*namespace, *message.package])

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

        for type in types:
            if type in PRIMITIVE_TYPE_MAP:
                pass
            else:
                dependentMessage = self.getMessageFromType(message, type, messageDB)
                if dependentMessage is None:
                    imports.append("// MISSING TYPE: {}".format(type))
                    continue
                self.generateFile(dependentMessage, messageDB, settings)

                imports.append(self.dependencyTemplate.substitute({
                    "package": self.determineNamespace(dependentMessage, settings),
                }))

        if settings['common_base']:
            imports.append("using {};".format(settings['common_base_namespace']))

        imports = list(set(imports))
        return '\n'.join(imports)

    def generateConstants(self, message: MessageData, messageDB: Dict[str, MessageData], settings: Dict) -> str:
        constants = []
        for field in message.fields:
            if field.constant_value is not None:
                constants.append(self.constantTemplate.substitute({
                    "name": self.sanitizeFieldName(field.field_name),
                    "type": PRIMITIVE_TYPE_MAP[field.field_type],
                    "value": "{}{}".format(str(field.constant_value), PRIMITIVE_SUFFIX_MAP[field.field_type])
                    if not isinstance(field.constant_value, str) else '"{}"'.format(field.constant_value),
                }))

        return '\n        '.join(constants)

    def generateFields(self, message, messageDB, settings):
        constants = []
        for field in message.fields:
            if field.is_array:
                if field.array_fixed_length < 0:
                    if field.field_type in PRIMITIVE_TYPE_MAP:
                        constants.append(self.fieldTemplate.substitute({
                            "name": self.sanitizeFieldName(field.field_name),
                            "type": "List<{}>".format(PRIMITIVE_TYPE_MAP[field.field_type])
                        }))
                    else:
                        dependentMessage = self.getMessageFromType(message, field.field_type, messageDB)
                        type = self.determineAlias(dependentMessage, settings)

                        constants.append(self.fieldTemplate.substitute({
                            "name": self.sanitizeFieldName(field.field_name),
                            "type": "List<{}>".format(type)
                        }))
                    # list
                else:
                    if field.field_type in PRIMITIVE_TYPE_MAP:
                        constants.append(self.fieldTemplate.substitute({
                            "name": self.sanitizeFieldName(field.field_name),
                            "type": "{}[]".format(PRIMITIVE_TYPE_MAP[field.field_type], field.array_fixed_length)
                        }))
                    else:
                        dependentMessage = self.getMessageFromType(message, field.field_type, messageDB)
                        type = self.determineAlias(dependentMessage, settings)

                        constants.append(self.fieldTemplate.substitute({
                            "name": self.sanitizeFieldName(field.field_name),
                            "type": "{}[]".format(type, field.array_fixed_length)
                        }))
                    #array

            else:
                if field.constant_value is None:
                    if field.field_type in PRIMITIVE_TYPE_MAP:
                        constants.append(self.fieldTemplate.substitute({
                            "name": self.sanitizeFieldName(field.field_name),
                            "type": PRIMITIVE_TYPE_MAP[field.field_type]
                        }))
                    else:
                        dependentMessage = self.getMessageFromType(message, field.field_type, messageDB)
                        type = self.determineAlias(dependentMessage, settings)

                        constants.append(self.fieldTemplate.substitute({
                            "name": self.sanitizeFieldName(field.field_name),
                            "type": type
                        }))

        return '\n        '.join(constants)

    def generateConstructor(self, message: MessageData, messageDB: Dict[str, MessageData], settings: Dict) -> str:
        args = []
        content = []

        for field in message.fields:
            if field.constant_value is None:
                content.append("this.{} = {};".format(self.sanitizeFieldName(field.field_name), self.sanitizeFieldName(field.field_name)))
                if field.is_array:
                    if field.array_fixed_length < 0:
                        if field.field_type in PRIMITIVE_TYPE_MAP:
                            args.append("List<{}> {} = null".format(PRIMITIVE_TYPE_MAP[field.field_type],
                                                                               self.sanitizeFieldName(field.field_name),
                                                                               PRIMITIVE_TYPE_MAP[field.field_type]))
                        else:
                            dependentMessage = self.getMessageFromType(message, field.field_type, messageDB)
                            type = self.determineAlias(dependentMessage, settings)

                            args.append("List<{}> {} = null".format(type,
                                                                              self.sanitizeFieldName(field.field_name),
                                                                              type))
                        # list
                    else:
                        if field.field_type in PRIMITIVE_TYPE_MAP:
                            args.append("{}[] {} = null".format(PRIMITIVE_TYPE_MAP[field.field_type],
                                                                              self.sanitizeFieldName(field.field_name)))
                        else:
                            dependentMessage = self.getMessageFromType(message, field.field_type, messageDB)
                            type = self.determineAlias(dependentMessage, settings)

                            args.append("{}[] {} = null".format(type, self.sanitizeFieldName(field.field_name)))
                        # array

                else:
                    if field.field_type in PRIMITIVE_TYPE_MAP:
                        args.append("{} {} = {}{}".format(PRIMITIVE_TYPE_MAP[field.field_type], self.sanitizeFieldName(field.field_name),
                                                        PRIMITIVE_DEFAULT_VALUE_MAP[field.field_type],
                                                          PRIMITIVE_SUFFIX_MAP[field.field_type]))
                    else:
                        dependentMessage = self.getMessageFromType(message, field.field_type, messageDB)
                        type = self.determineAlias(dependentMessage, settings)

                        args.append("{} {} = null".format(type, self.sanitizeFieldName(field.field_name)))

        variables = {
            "msgID": message.getID(),
            "args": ", ".join(args),
            "classname": self.determineClassName(message, settings),
            "superargs": "",
            "content": "\n            ".join(content),
        }

        return self.constructorTemplate.substitute(variables)

    def generateSerializers(self, message: MessageData, messageDB: Dict[str, MessageData], settings: Dict) -> str:
        serializers = []
        for field in message.fields:
            if field.constant_value is not None:
                continue
            if field.is_array:
                if field.array_fixed_length < 0:
                    # dynamic length array
                    if field.field_type in PRIMITIVE_SERIALISATION_MAP:
                        serializers.append("message.{}s(this.{}.ToArray());".format(PRIMITIVE_SERIALISATION_MAP[field.field_type],
                                                                        self.sanitizeFieldName(field.field_name)))
                    elif field.field_type == 'time':
                        serializers.append("AddArrayLength(message, this.{}.Count);".format(self.sanitizeFieldName(field.field_name)))

                        serializers.append("for (int i = 0; i < this.{}.Count; i++) {{".format(self.sanitizeFieldName(field.field_name)))
                        serializers.append("    message.AddUInt(this.{}[i][0]);".format(self.sanitizeFieldName(field.field_name)))
                        serializers.append("    message.AddUInt(this.{}[i][1]);".format(self.sanitizeFieldName(field.field_name)))
                        serializers.append("}")
                    elif field.field_type == 'duration':
                        serializers.append("AddArrayLength(message, this.{}.Count);".format(self.sanitizeFieldName(field.field_name)))

                        serializers.append("for (int i = 0; i < this.{}.Count; i++) {{".format(self.sanitizeFieldName(field.field_name)))
                        serializers.append("    message.AddInt(this.{}[i][0]);".format(self.sanitizeFieldName(field.field_name)))
                        serializers.append("    message.AddInt(this.{}[i][1]);".format(self.sanitizeFieldName(field.field_name)))
                        serializers.append("}")
                    else:
                        serializers.append("AddArrayLength(message, this.{}.Count);".format(self.sanitizeFieldName(field.field_name)))
                        serializers.append("for (int i = 0; i < this.{}.Count; i++) {{".format(self.sanitizeFieldName(field.field_name)))
                        serializers.append("    this.{}[i].serializeToMessage(message);".format(self.sanitizeFieldName(field.field_name)))
                        serializers.append("}")
                else:
                    #fixed size array
                    if field.field_type in PRIMITIVE_SERIALISATION_MAP:
                        serializers.append(
                            "message.{}s(this.{}, false);".format(PRIMITIVE_SERIALISATION_MAP[field.field_type],
                                                              self.sanitizeFieldName(field.field_name)))
                    elif field.field_type == 'time':
                        serializers.append("for (int i = 0; i < {}; i++) {{".format(field.array_fixed_length))
                        serializers.append("    message.AddUInt(this.{}[i][0]);".format(self.sanitizeFieldName(field.field_name)))
                        serializers.append("    message.AddUInt(this.{}[i][1]);".format(self.sanitizeFieldName(field.field_name)))
                        serializers.append("}")
                    elif field.field_type == 'duration':
                        serializers.append("for (int i = 0; i < {}; i++) {{".format(field.array_fixed_length))
                        serializers.append("    message.AddInt(this.{}[i][0]);".format(self.sanitizeFieldName(field.field_name)))
                        serializers.append("    message.AddInt(this.{}[i][1]);".format(self.sanitizeFieldName(field.field_name)))
                        serializers.append("}")
                    else:
                        serializers.append("for (int i = 0; i < {}; i++) {{".format(field.array_fixed_length))
                        serializers.append("    this.{}[i].serializeToMessage(message);".format(self.sanitizeFieldName(field.field_name)))
                        serializers.append("}")
            else:
                if field.field_type in PRIMITIVE_SERIALISATION_MAP:
                    serializers.append("message.{}(this.{});".format(PRIMITIVE_SERIALISATION_MAP[field.field_type],
                                                                    self.sanitizeFieldName(field.field_name)))
                elif field.field_type == 'time':
                    serializers.append("message.AddUInt(this.{}[0]);".format(self.sanitizeFieldName(field.field_name)))
                    serializers.append("message.AddUInt(this.{}[1]);".format(self.sanitizeFieldName(field.field_name)))
                elif field.field_type == 'duration':
                    serializers.append("message.AddInt(this.{}[0]);".format(self.sanitizeFieldName(field.field_name)))
                    serializers.append("message.AddInt(this.{}[1]);".format(self.sanitizeFieldName(field.field_name)))
                else:
                    serializers.append("this.{}.serializeToMessage(message);".format(self.sanitizeFieldName(field.field_name)))

        return "\n            ".join(serializers)

    def generateDeserializers(self, message: MessageData, messageDB: Dict[str, MessageData], settings: Dict) -> str:
        deserializers = []
        isLengthDeclared = False

        for field in message.fields:
            if field.constant_value is not None:
                continue
            if field.is_array:
                if field.array_fixed_length < 0:
                    # dynamic length array
                    if field.field_type in PRIMITIVE_DESERIALISATION_MAP:
                        deserializers.append("this.{} = new List<{}>(message.{}s());".format(self.sanitizeFieldName(field.field_name),
                                                                                            PRIMITIVE_TYPE_MAP[field.field_type],
                                                                                            PRIMITIVE_DESERIALISATION_MAP[field.field_type]))
                    elif field.field_type == 'time':
                        if not isLengthDeclared:
                            deserializers.append("int length = ReadArrayLength(message);")
                            isLengthDeclared = True
                        else:
                            deserializers.append("length = ReadArrayLength(message);")

                        deserializers.append("this.{} = new List<uint[]>();".format(self.sanitizeFieldName(field.field_name)))
                        deserializers.append("for (int i = 0; i < length; i++) {")
                        deserializers.append("    this.{}.Add(new uint[]{{message.GetUInt(), message.GetUInt()}});".format(self.sanitizeFieldName(field.field_name)))
                        deserializers.append("}")

                    elif field.field_type == 'duration':
                        if not isLengthDeclared:
                            deserializers.append("int length = ReadArrayLength(message);")
                            isLengthDeclared = True
                        else:
                            deserializers.append("length = ReadArrayLength(message);")

                        deserializers.append("this.{} = new List<int[]>();".format(self.sanitizeFieldName(field.field_name)))
                        deserializers.append("for (int i = 0; i < length; i++) {")
                        deserializers.append(
                            "    this.{}.Add(new int[]{{message.GetInt(), message.GetInt()}});".format(
                                self.sanitizeFieldName(field.field_name)))
                        deserializers.append("}")
                    else:
                        if not isLengthDeclared:
                            deserializers.append("int length = ReadArrayLength(message);")
                            isLengthDeclared = True
                        else:
                            deserializers.append("length = ReadArrayLength(message);")

                        dependentMessage = self.getMessageFromType(message, field.field_type, messageDB)
                        type = self.determineAlias(dependentMessage, settings)

                        deserializers.append("this.{} = new List<{}>();".format(self.sanitizeFieldName(field.field_name), type))
                        deserializers.append("for (int i = 0; i < length; i++) {")

                        deserializers.append("    {} value = new {}();".format(type, type))
                        deserializers.append("    value.deserializeFromMessage(message);")
                        deserializers.append("    this.{}.Add(value);".format(self.sanitizeFieldName(field.field_name)))
                        deserializers.append("}")
                else:
                    #fixed size array
                    if field.field_type in PRIMITIVE_DESERIALISATION_MAP:
                        deserializers.append("message.{}s({}, this.{});".format(PRIMITIVE_DESERIALISATION_MAP[
                                                                                      field.field_type],
                                                                                           field.array_fixed_length,
                                                                                   self.sanitizeFieldName(field.field_name)))
                    elif field.field_type == 'time':

                        deserializers.append("this.{} = new uint[{}][2];".format(self.sanitizeFieldName(field.field_name), field.array_fixed_length))
                        deserializers.append("for (int i = 0; i < {}; i++)  {{".format(field.array_fixed_length))
                        deserializers.append(
                            "    this.{}[i] = new uint[]{{message.GetUInt(), message.GetUInt()}};".format(self.sanitizeFieldName(field.field_name)))
                        deserializers.append("}")

                    elif field.field_type == 'duration':
                        deserializers.append(
                            "this.{} = new int[{}][2]();".format(self.sanitizeFieldName(field.field_name), field.array_fixed_length))
                        deserializers.append("for (int i = 0; i < {}; i++)  {{".format(field.array_fixed_length))
                        deserializers.append(
                            "    this.{}[i] = new int[]{{message.GetInt(), message.GetInt()}};".format(
                                self.sanitizeFieldName(field.field_name)))
                        deserializers.append("}")
                    else:

                        dependentMessage = self.getMessageFromType(message, field.field_type, messageDB)
                        type = self.determineAlias(dependentMessage, settings)

                        deserializers.append("this.{} = new {}[{}]();".format(self.sanitizeFieldName(field.field_name), type, field.array_fixed_length))
                        deserializers.append("for (int i = 0; i < {}; i++)  {{".format(field.array_fixed_length))

                        deserializers.append("    {} value = new {}();".format(type, type))
                        deserializers.append("    value.deserializeFromMessage(message);")
                        deserializers.append("    this.{}[i] = value;".format(self.sanitizeFieldName(field.field_name)))
                        deserializers.append("}")
            else:
                if field.field_type in PRIMITIVE_DESERIALISATION_MAP:
                    deserializers.append("this.{} = message.{}();".format(self.sanitizeFieldName(field.field_name), PRIMITIVE_DESERIALISATION_MAP[field.field_type]))
                elif field.field_type == 'time':
                    deserializers.append("this.{} = new uint[]{{message.GetUInt(), message.GetUInt()}};".format(self.sanitizeFieldName(field.field_name)))
                elif field.field_type == 'duration':
                    deserializers.append("this.{} = new int[]{{message.GetInt(), message.GetInt()}};".format(self.sanitizeFieldName(field.field_name)))
                else:
                    dependentMessage = self.getMessageFromType(message, field.field_type, messageDB)
                    type = self.determineAlias(dependentMessage, settings)
                    deserializers.append("this.{} = new {}();".format(self.sanitizeFieldName(field.field_name), type))
                    deserializers.append("this.{}.deserializeFromMessage(message);".format(self.sanitizeFieldName(field.field_name)))

        return "\n            ".join(deserializers)

    def checkPackage(self, path):
        if not exists(path):
            makedirs(path)

    def writeOutFiles(self, base_path: str, settings: Dict):
        for msgID in self.generated_messages:
            source, message = self.generated_messages[msgID]

            messagePath = base_path + "/riptide"

            if not exists(messagePath):
                makedirs(messagePath)

            basePackage = settings['namespace'].split('.')

            for package in basePackage:
                messagePath += '/' + package
                self.checkPackage(messagePath)

            for package in message.package:
                messagePath += '/' + package
                self.checkPackage(messagePath)

            writeFile("{}/{}.cs".format(messagePath, message.name), source)

    def clear(self):
        self.messages_names.clear()
        self.generated_messages.clear()

