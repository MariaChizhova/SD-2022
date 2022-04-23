from enum import Enum


class Type(Enum):
    """
    Class that represents types of tokens
    """
    STRING = 1
    CLEAN_STRING = 2
    DECLARATION = 4
    PIPE = 5
    END = 6


class Token:
    """
    Class that represents token
    """
    def __init__(self, value: str, token_type: Type):
        """
        Constructor
        :param value: token value
        :param token_type: token type
        """
        self.value = value
        self.type = token_type

    def getValue(self):
        """
        :return: token value
        """
        return self.value

    def getType(self):
        """
        :return: token type
        """
        return self.type

    def __repr__(self):
        """
        overriding represent method
        """
        return f'{self.type}({self.value})'

    def __eq__(self, other):
        """
        overriding equal method
        """
        if isinstance(other, self.__class__):
            return self.value == other.value and self.type == other.type
        else:
            return False
