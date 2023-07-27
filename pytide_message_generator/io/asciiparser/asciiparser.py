from typing import Tuple, Callable, Dict, List

DECIMAL_POINT: str = '.'

DECIMAL_DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
HEXADECIMAL_DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']

ESCAPE_SEQUENCES = {
    '"': '"',
    '\\': '\\',
    '/': '/',
    'b': '\b',
    'f': '\f',
    'n': '\n',
    'r': '\r',
    't': '\t',
}


class AsciiParserException(Exception):

    def __init__(self, pos: Tuple[int, int, int], msg: str):
        self.pos = pos
        self.msg = msg

    def __str__(self):
        return "{} at line {}, char {} ({})".format(self.msg, self.pos[0], self.pos[1], self.pos[2])


class AsciiParser:

    def __init__(self, data: str = ""):
        self.__nextPos: int = 0
        self.data: str = data

    def loadData(self, data: str):
        self.__nextPos = 0
        self.data = data

    def reset(self):
        self.__nextPos = 0

    def getLinePosition(self, position: int = None) -> Tuple[int, int, int]:
        if position is None:
            position = self.__nextPos

        line = 1
        char = 1

        for i in range(position):
            if self.data[i] == '\n':
                line += 1
                char = 1
            else:
                char += 1

        return (line, char, position)

    def available(self) -> bool:
        return self.__nextPos < len(self.data)

    def peek(self):
        if not self.available():
            raise AsciiParserException(self.getLinePosition(), "Unexpected EOF")
        return self.data[self.__nextPos]

    def read(self):
        if not self.available():
            raise AsciiParserException(self.getLinePosition(), "Unexpected EOF")
        self.__nextPos += 1
        return self.data[self.__nextPos-1]

    def consume(self):
        if not self.available():
            raise AsciiParserException(self.getLinePosition(), "Unexpected EOF")
        self.__nextPos += 1

    def check(self, c: str):
        if len(c) > 1:
            raise ValueError("Expected single char, but got '{}'. Please use validate(str) instead".format(c))
        elif c is not self.peek():
            raise AsciiParserException(self.getLinePosition(), "Char {} expected, but got {}".format(c, self.peek()))

    def validate(self, expected: str):
        for c in expected:
            if c is not self.peek():
                raise AsciiParserException(self.getLinePosition(),
                                           "Char {} expected, but got {}".format(c, self.peek()))
            self.consume()

    def skipWhitespace(self) -> int:
        whiteSpaces = 0

        while self.available():
            c = self.peek()
            if c.isspace():
                self.consume()
                whiteSpaces += 1
            else:
                return whiteSpaces
        return whiteSpaces

    def skipCharacters(self, skipChars=None) -> int:
        if skipChars is None:
            skipChars = [' ', '\t']

        skippedChars = 0

        while self.available():
            c = self.peek()
            if c in skipChars:
                self.consume()
                skippedChars += 1
            else:
                return skippedChars
        return skippedChars

    def readHexInteger(self, expectedDigits: int) -> int:
        self.skipWhitespace()

        c = self.peek()
        if c == '-':
            self.consume()
            self.skipWhitespace()
            c = self.read()
            value = -self.getHexNumberFromChar(c)
        else:
            value = self.getHexNumberFromChar(c)
            self.consume()

        for i in range(expectedDigits):
            c = self.peek()
            value *= 16
            value += self.getHexNumberFromChar(c)
            self.consume()

        return value

    def readToWhitespace(self):
        sb = []
        while True:
            c = self.peek()
            if c.isspace():
                return ''.join(sb)
            sb.append(c)
            self.consume()

            if not self.available():
                return ''.join(sb)

    def readToSeperator(self, seperator: List[str]):
        sb = []
        while True:
            c = self.peek()
            if c in seperator:
                return ''.join(sb)
            sb.append(c)
            self.consume()

            if not self.available():
                return ''.join(sb)

    def readToEndOfLine(self):
        sb = []
        while True:
            if not self.available():
                return ''.join(sb)
            c = self.peek()
            if c == '\n':
                return ''.join(sb)
            sb.append(c)
            self.consume()

    def readToEndOfFile(self):
        pos = self.__nextPos
        self.__nextPos = len(self.data)
        return self.data[pos:]

    def readInteger(self) -> int:
        self.skipWhitespace()

        c = self.peek()
        if c == '-':
            self.consume()
            self.skipWhitespace()
            c = self.read()
            value = -self.getNumberFromChar(c)
        else:
            value = self.getNumberFromChar(c)
            self.consume()

        while True:
            if not self.available():
                return value
            c = self.peek()
            if not self.isDigit(c):
                return value

            value *= 10
            value += self.getHexNumberFromChar(c)
            self.consume()

    def readFloat(self) -> float:
        value = 0
        divisor = 1
        mul = 1
        countDivisor = False

        self.skipWhitespace()

        c = self.peek()
        if c == '-':
            self.consume()
            self.skipWhitespace()
            mul = -1
            c = self.peek()

        if c == DECIMAL_POINT:
            countDivisor = True
            self.consume()
            c = self.peek()

        value = self.getNumberFromChar(c)
        if countDivisor:
            divisor *= 10
        self.consume()

        while True:
            if not self.available():
                break
            c = self.peek()
            if self.isDigit(c):
                value *= 10
                value += self.getNumberFromChar(c)
                self.consume()
                if countDivisor:
                    divisor *= 10
            elif c == DECIMAL_POINT:
                countDivisor = True
                self.consume()
            else:
                break
        c = self.peek()
        if c in ['e', 'E']:
            self.consume()
            exp = self.readInteger()
            mul *= 10**exp

        return (float(value)/divisor)*mul

    def readBool(self) -> bool:
        self.skipWhitespace()
        c = self.peek()
        pos = self.__nextPos
        try:
            if c in ['T', 't']:
                self.consume()
                self.validate('rue')
                return True
            elif c in ['F', 'f']:
                self.consume()
                self.validate('alse')
                return False
            else:
                raise AsciiParserException((0, 0, 0), "")
        except AsciiParserException as ex:
            raise AsciiParserException(self.getLinePosition(pos), "Expected boolean value ('True', 'true', 'False' or 'false')")

    def readStringLiteral(self) -> str:
        self.skipWhitespace()
        self.check('"')
        self.consume()

        chars = []

        while True:
            c = self.peek()
            if c == '"':
                self.consume()
                return ''.join(chars)
            elif c == '\\':
                self.consume()
                c = self.read()
                if c in ESCAPE_SEQUENCES:
                    chars.append(ESCAPE_SEQUENCES[c])
                elif c == 'u':
                    codepoint = self.readHexInteger(4)
                    chars.append(chr(codepoint))
                else:
                    raise AsciiParserException(self.getLinePosition(), "Invalid escape sequence: '\\{}'".format(c))
            else:
                chars.append(c)
                self.consume()

    def isDigit(self, c: str):
        if len(c) > 1:
            raise ValueError("Expected single char, but got '{}' instead".format(c))
        return c in DECIMAL_DIGITS

    def isHexDigit(self, c: str):
        if len(c) > 1:
            raise ValueError("Expected single char, but got '{}' instead".format(c))
        return c.lower() in HEXADECIMAL_DIGITS

    def getNumberFromChar(self, c: str) -> int:
        if len(c) > 1:
            raise ValueError("Expected single char, but got '{}' instead".format(c))
        elif c in DECIMAL_DIGITS:
            return DECIMAL_DIGITS.index(c)
        else:
            raise AsciiParserException(self.getLinePosition(), "Expected decimal digit (0 - 9), but got '{}' instead.".format(c))

    def getHexNumberFromChar(self, c: str) -> int:
        if len(c) > 1:
            raise ValueError("Expected single char, but got '{}' instead".format(c))
        elif c.lower() in HEXADECIMAL_DIGITS:
            return HEXADECIMAL_DIGITS.index(c.lower())
        else:
            raise AsciiParserException(self.getLinePosition(),
                                       "Expected hexadecimal digit (0 - f), but got '{}' instead.".format(c))
