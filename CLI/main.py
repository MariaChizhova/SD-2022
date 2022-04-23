import sys
import io
from typing import Any
from CLI.parser import Parser


class CLI:
    """
    Class which represents CLI interpreter.
    """

    def __init__(self):
        """
        Constructor
        """
        self.vars = {}
        self.is_running = True

    def process(self, line: str, stdin: Any, stdout: Any):
        """
        Executes the passed command
        :param line: str - the command to be executed
        :param stdin: the file object to be used as input for the command
        :param stdout: the file object to be used as the output for the command
        :return: None
        :raise SystemExit: when executing the Exit command
        """
        io_in = stdin
        io_out = io.StringIO()
        parser = Parser(line, self.vars)
        commandsList = parser.parse()
        for command in commandsList:
            self.is_running = not command.execute(io_in, io_out)
            io_in = io_out
            io_in.seek(0, 0)
            io_out = io.StringIO()
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
