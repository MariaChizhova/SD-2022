import sys
import io
from typing import Any
from CLI.parser import Parser
from CLI.commands import Exit, Declaration


class CLI:
    """
    Class which represents CLI interpreter.
    """

    pipe_ignore = {
        Exit, Declaration
    }

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
        commands_list = parser.parse()
        if len(commands_list) == 0:
            return
        for command in commands_list:
            if len(commands_list) > 1 and type(command) in self.pipe_ignore:
                continue
            self.is_running = not command.execute(io_in, io_out)
            io_in = io_out
            io_in.seek(0, 0)
            io_out = io.StringIO()
        output = io_in.read()
        if output:
            stdout.write(output)
            stdout.write('\n')


if __name__ == '__main__':
    cli = CLI()
    print('> ', end='')
    sys.stdout.flush()
    for line in sys.stdin:
        line = line.rstrip('\n')
        if line != '':
            cli.process(line, sys.stdin, sys.stdout)
            sys.stderr.flush()
        if not cli.is_running:
            print("CLI exit")
            break
        print('> ', end='', flush=True)
