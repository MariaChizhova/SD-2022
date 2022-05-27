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
        (Type.STRING, r'(\"[^\"]*\")|([\\\w\-\.\!\@\?\#\$\%\^\&\/\*\(\)\-\+:]+)'),
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

    def parse_commands(self, tokens: List[Token]) -> List[Command]:
        """
        Converts a tokens to a commands
        :param tokens: list of tokens of type CLEAN_STRING
        :return list of Command Instances
        :raise AttributeError: invalid arguments for the command
        """
        commands_map = {
            'cat': commands.Cat,
            'echo': commands.Echo,
            'wc': commands.Wc,
            'pwd': commands.Pwd,
            'exit': commands.Exit,
            'grep': commands.Grep,
            'ls': commands.Ls,
            'cd': commands.Cd
        }
        commands_list = []
        pos = 0
        begin = pos
        while pos < len(tokens):
            if tokens[pos].type == Type.PIPE or tokens[pos].type == Type.END:
                if pos - begin > 0:
                    try:
                        tokens_command = tokens[begin:pos]
                        if len(tokens_command) >= 3 and tokens_command[1].type == Type.DECLARATION:
                            commands_list.append(commands.Declaration(
                                [self.variables, tokens_command[0].value, tokens_command[2].value]))
                            begin = pos + 1
                            continue
                        com_name = tokens_command[0].value
                        args = [i.value for i in tokens_command[1:]]
                        if com_name not in commands_map:
                            commands_list.append(commands.External([com_name, self.variables] + args))
                        else:
                            commands_list.append(commands_map[com_name](args))
                    except AttributeError as e:
                        print(e)
                        return []
                begin = pos + 1
            pos += 1
        return commands_list

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
            try:
                val = self.next_token()
                res.append(val)
            except AssertionError as e:
                print(*e.args)
                return []
        return self.parse_commands([self.substitution(t) for t in res])
