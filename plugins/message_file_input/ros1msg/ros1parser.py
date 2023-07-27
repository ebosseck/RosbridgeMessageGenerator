from typing import Tuple, List, Dict, Optional

from pytide_message_generator.dataprovider.field_data import FieldData
from pytide_message_generator.dataprovider.message_data import MessageData
from pytide_message_generator.io.asciiparser.asciiparser import AsciiParser, AsciiParserException
from pytide_message_generator.io.filewriter import readFile

ROS_MSG_PRIMITIVES = ["bool", "int8", "uint8", "int16", "uint16", "int32", "uint32", "int64", "uint64", "float32",
                      "float64", "string", "time", "duration"]

ROS_NAME_START = ['a', 'A', 'b', 'B', 'c', 'C', 'd', 'D', 'e', 'E', 'f', 'F', 'g', 'G', 'h', 'H', 'i', 'I', 'j', 'J',
                  'k', 'K', 'l', 'L', 'm', 'M', 'n', 'N', 'o', 'O', 'p', 'P', 'q', 'Q', 'r', 'R', 's', 'S', 't', 'T',
                  'u', 'U', 'v', 'V', 'w', 'W', 'x', 'X', 'y', 'Y', 'z', 'Z']


ROS_NAME = ['a', 'A', 'b', 'B', 'c', 'C', 'd', 'D', 'e', 'E', 'f', 'F', 'g', 'G', 'h', 'H', 'i', 'I', 'j', 'J',
            'k', 'K', 'l', 'L', 'm', 'M', 'n', 'N', 'o', 'O', 'p', 'P', 'q', 'Q', 'r', 'R', 's', 'S', 't', 'T',
            'u', 'U', 'v', 'V', 'w', 'W', 'x', 'X', 'y', 'Y', 'z', 'Z', '0', '1', '2', '3', '4', '5', '6', '7',
            '8', '9', '_']

MESSAGE_TYPE_ALIASSES = {
    "Header": "std_msgs/Header",
    "char": "uint8",
    "byte": "int8",
}

class Ros1Parser(AsciiParser):

    def __init__(self, data=""):
        super(Ros1Parser, self).__init__(data=data)

        self.message_names = []
        self.localMessageNames: Dict[str, List[str]] = {}

    def buildTypeChecks (self, types: List[Tuple[str, str, str]]):

        for type in types:
            self.message_names.append("/".join(type[:2]))
            if type[0] not in self.localMessageNames:
                self.localMessageNames[type[0]] = []
            self.localMessageNames[type[0]].append(type[1])

    def parseMessage(self, package: str, name: str, path: str) -> MessageData:
        message = readFile(path)
        print("Processing File: {}".format(path))
        self.loadData(message)
        fields: List[FieldData] = []

        self.skipWhitespace()
        while self.available():
            field, new_msg = self.parseField()
            if field is not None:
                fields.append(field)
            self.skipWhitespace()

        return MessageData([package], name, fields)

    def parseService(self, package: str, name: str, path: str) -> List[MessageData]:
        message = readFile(path)
        print("Processing File: {}".format(path))
        self.loadData(message)
        fields: List[FieldData] = []

        self.skipWhitespace()

        messages = []

        while self.available():
            field, new_msg = self.parseField()
            if field is not None:
                fields.append(field)

            if new_msg:
                messages.append(MessageData([package], "{}Request".format(name), fields))
                fields = []

            self.skipWhitespace()

        messages.append(MessageData([package], "{}Response".format(name), fields))

        messages[0].srv_siblings = [messages[1]]
        messages[0].srv_name = name
        messages[0].srv_index = 0

        messages[1].srv_siblings = [messages[0]]
        messages[1].srv_name = name
        messages[1].srv_index = 1

        return messages

    def parseField(self) -> Tuple[Optional[FieldData], bool]:

        comments = []

        while self.available():
            c = self.peek()
            if c == '#':
                # Comment
                self.consume()
                comments.append(self.readToEndOfLine().strip())
            elif c == '-':
                self.validate('---')
                return None, True
            else:
                field_type = self.readToSeperator([' ', '['])
                if field_type in MESSAGE_TYPE_ALIASSES:
                    field_type = MESSAGE_TYPE_ALIASSES[field_type]
                self.skipWhitespace()
                c = self.peek()

                isArray = False
                fixedLength = -1
                constantValue = None

                if c == '[':
                    isArray = True
                    self.consume()
                    self.skipWhitespace()
                    c =self.peek()
                    if c != ']':
                        fixedLength = self.readInteger()
                        self.skipWhitespace()
                        self.check(']')
                    self.consume()
                    self.skipWhitespace()

                field_name = self.readFieldName()
                self.skipCharacters()

                if self.available():
                    c = self.peek()
                    if c == '=':
                        # Constant
                        self.consume()
                        self.skipCharacters()
                        constantValue = self.readConstantValue(field_type)
                        self.skipCharacters()
                        if self.available():
                            c = self.peek()

                    if c == '#':
                        self.consume()
                        comments.append(self.readToEndOfLine().strip())

                #print("Field Type: {}".format(field_type))
                #print("IsArray: {}".format(isArray))
                #print("Field Name: {}".format(field_name))
                eol = self.readToEndOfLine().strip()
                if eol != '':
                    print("Rest of Line: {}".format(eol))
                return FieldData(field_type, field_name, isArray, array_fixed_length=fixedLength,
                                 constant_value=constantValue, comment="\n".join(comments)), False
            self.skipWhitespace()

        return None, False

    def readConstantValue(self, expected_type):
        if expected_type == 'bool':
            return self.readBool()
        elif expected_type in ["int8", "uint8", "int16", "uint16", "int32", "uint32", "int64", "uint64"]:
            return self.readInteger()
        elif expected_type in ["float32", "float64"]:
            return self.readFloat()
        elif expected_type == "string":
            return self.readToEndOfLine()
        else:
            raise AsciiParserException(self.getLinePosition(), "Invalid type for constant: {}".format(expected_type))

    def readFieldName(self):
        sb = []

        c = self.peek()
        if c not in ROS_NAME_START:
            raise AsciiParserException(self.getLinePosition(), "Expected [a-z, A-Z], but got {} instead.".format(c))

        while True:
            c = self.peek()
            if c not in ROS_NAME:
                return ''.join(sb)
            sb.append(c)
            self.consume()

            if not self.available():
                return ''.join(sb)
