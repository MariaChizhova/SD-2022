import sys
import io
from typing import List, Any
from CLI.parser import Parser
from CLI.token_types import Token, Type
from CLI.commands import Command
import CLI.commands as commands
import re


class CLI:
    """
    Class which represents CLI interpreter.
    """

    def __init__(self):
        self.vars = {}
        self.is_running = True

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
                    new_str += self.vars.get(var_name, '')
                else:
                    break
            new_str += token.value[pos:]
            return Token(new_str, Type.CLEAN_STRING)
        else:
            return token

    def parseCommand(self, tokens: List[Token]) -> Command:
        """
        Converts a token to a command
        :param tokens: tokens of type CLEAN_STRING
        :return Command Instance
        :raise AttributeError: invalid arguments for the command
        """
        d = {
            'cat': commands.Cat,
            'echo': commands.Echo,
            'wc': commands.Wc,
            'pwd': commands.Pwd,
            'exit': commands.Exit
        }
        com_name = tokens[0].value
        args = [i.value for i in tokens[1:]]
        if com_name not in d:
            return commands.External([com_name, self.vars] + args)
        else:
            return d[com_name](args)

    def process(self, line: str, stdin: Any, stdout: Any):
        """
        Executes the passed command
        :param line: str - the command to be executed
        :param stdin: the file object to be used as input for the command
        :param stdout: the file object to be used as the output for the command
        :return: None
        :raise SystemExit: when executing the Exit command
        """
        parser = Parser(line)
        tokens = [self.substitution(t) for t in parser.parse()]
        if len(tokens) >= 3 and tokens[1].type == Type.DECLARATION:
            command = commands.Declaration([self.vars, tokens[0].value, tokens[2].value])
            command.execute(stdin, stdout)
            return
        io_in = stdin
        io_out = io.StringIO()
        pos = 0
        begin = pos
        while pos < len(tokens):
            if tokens[pos].type == Type.PIPE or tokens[pos].type == Type.END:
                if len(tokens[begin:pos]) > 0:
                    try:
                        command = self.parseCommand(tokens[begin:pos])
                        self.is_running = not command.execute(io_in, io_out)
                        io_in = io_out
                        io_in.seek(0, 0)
                        io_out = io.StringIO()
                        begin = pos + 1
                    except AttributeError as e:
                        print(e)
            pos += 1
        stdout.write(io_in.read())
        stdout.write('\n')


if __name__ == '__main__':
    cli = CLI()
    print('> ', end='')
    sys.stdout.flush()
    for line in sys.stdin:
        line = line.rstrip('\n')
        if line != '':
            cli.process(line, sys.stdin, sys.stdout)
        if not cli.is_running:
            print("CLI exit")
            break
        print('> ', end='')
        sys.stdout.flush()
