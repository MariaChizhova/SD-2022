from typing import List
from CLI.token_types import Type, Token
from collections import OrderedDict
import re
from CLI.commands import Command
import CLI.commands as commands


class Parser:
    """Class for parsing the string"""

    tokens = OrderedDict([
        (Type.PIPE, r'\|'),
        (Type.DECLARATION, r'='),
        (Type.CLEAN_STRING, r'\'[^\']*\''),
        (Type.STRING, r'(\"[^\"]*\")|([\w\-\.\!\@\?\#\$\%\^\&\/\*\(\)\-\+]+)'),
        (Type.END, chr(0))
    ])

    def __init__(self, string: str, variables: dict):
        """
        Parser Constructor
        :param string: line for parsing
        :param variables: stored variable dictionary
        """
        self.string = string + chr(0)
        self.pos = 0
        self.n = len(self.string)
        self.variables = variables

    def _skip_ws(self):
        """Private. Skips leading spaces.
        :return:None
        """
        while self.pos < self.n and self.string[self.pos].isspace():
            self.pos += 1

    def next_token(self) -> Token:
        """
        Parses the first token in the string.
        Skips leading spaces from the current position and parse the token
        :return: Next parsed token
        :raise AssertionError: if the token cannot be parsed
        """
        self._skip_ws()
        for key, value in self.tokens.items():
            match = re.match(value, self.string[self.pos:])
            if match is not None:
                self.pos = self.pos + match.end()
                if key == Type.CLEAN_STRING:
                    res = match.group(0)[1:-1]
                elif key == Type.STRING:
                    res = match.group(0)
                    if res[0] == '"':
                        res = res[1:-1]
                else:
                    res = match.group(0)
                return Token(res, key)
        raise AssertionError(f'Token not found, unparsed: "{self.string[self.pos:]}"')

    def parseCommands(self, tokens: List[Token]) -> List[Command]:
        """
        Converts a tokens to a commands
        :param tokens: list of tokens of type CLEAN_STRING
        :return list of Command Instances
        :raise AttributeError: invalid arguments for the command
        """
        d = {
            'cat': commands.Cat,
            'echo': commands.Echo,
            'wc': commands.Wc,
            'pwd': commands.Pwd,
            'exit': commands.Exit
        }
        if len(tokens) >= 3 and tokens[1].type == Type.DECLARATION:
            return [commands.Declaration([self.variables, tokens[0].value, tokens[2].value])]
        commandsList = []
        pos = 0
        begin = pos
        while pos < len(tokens):
            if tokens[pos].type == Type.PIPE or tokens[pos].type == Type.END:
                if len(tokens[begin:pos]) > 0:
                    try:
                        tokensCommand = tokens[begin:pos]
                        com_name = tokensCommand[0].value
                        args = [i.value for i in tokensCommand[1:]]
                        if com_name not in d:
                            commandsList.append(commands.External([com_name, self.variables] + args))
                        else:
                            commandsList.append(d[com_name](args))
                        begin = pos + 1
                    except AttributeError as e:
                        print(e)
            pos += 1
        return commandsList

    def substitution(self, token: Token) -> Token:
        """
        Performs variable substitution in the token, if it exists
        For STRING tokens, substitution of all variables is performed
        :param token: Token of any type
        :return: A token of the CLEAN_STRING type
        """
        if token.type == Type.STRING:
            new_str = ''
            pattern = re.compile(r'\$[a-zA-Z_][\w]*')
            pos = 0
            while True:
                match = pattern.search(token.value, pos)
                if match is not None:
                    new_str += token.value[pos:match.span()[0]]
                    pos = match.span()[1]
                    var_name = match.group(0)[1:]
                    new_str += self.variables.get(var_name, '')
                else:
                    break
            new_str += token.value[pos:]
            return Token(new_str, Type.CLEAN_STRING)
        else:
            return token

    def parse(self) -> List[Command]:
        """
        Parse all line
        :return: List of parsed commands
        :raise AssertionError: if the token cannot be parsed
        """
        res = []
        val = None
        while val is None or val.type != Type.END:
            val = self.next_token()
            res.append(val)
        return self.parseCommands([self.substitution(t) for t in res])
