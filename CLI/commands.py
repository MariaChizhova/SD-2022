import io
from abc import ABC, abstractmethod
from os import getcwd
from typing import List
import sys
import os
import subprocess as sb


class Command(ABC):
    """Abstract class command. Each command is inherited from this class"""

    @abstractmethod
    def __init__(self):
        """
        Constructor
        :param args: list of command arguments
        """
        pass

    @abstractmethod
    def execute(self, stdin, stdout):
        """
        Function executes command with the given arguments
        :param stdin: input stream
        :param stdout: ouput stream
        """
        pass


class Cat(Command):
    """Class which represents cat command"""

    def __init__(self, args: List[str]):
        """
        Constructor
        :param args: list of command arguments
        :raise AttributeError if the length of the args list is greater than 1
        """
        if len(args) > 1:
            raise AttributeError("Too many arguments")
        self.arg = args[0] if len(args) > 0 else None

    def cat(self, lines):
        """
        Function that cat given lines
        :param lines: input lines
        :return: None
        """
        for line in lines:
            print(line, file=self.stdout, end='')

    def cat_file(self, filename: str):
        """
        Print the content of the given file into output stream
        :param filename: name of the file
        :raise FileNotFoundError if the given file cannot be found
        :return: None
        """
        try:
            with open(filename) as lines:
                self.cat(lines)
        except FileNotFoundError:
            print(f'cat: {filename}: No such file or directory')

    def execute(self, stdin, stdout):
        """
        Function executes cat command
        :param stdin: input stream
        :param stdout: output stream
        :return: 0 - command was executed successfully
        """
        self.stdin = stdin
        self.stdout = stdout
        if not self.arg:
            self.cat(self.stdin.read().strip())
        else:
            self.cat_file(self.arg)
        return 0

    def __eq__(self, other):
        if isinstance(other, Cat):
            return self.arg == other.arg
        return False


class Echo(Command):
    """Class which represents echo command"""

    def __init__(self, args: List[str]):
        """
        Constructor
        :param args: list of command arguments
        """
        self.args = args

    def execute(self, stdin, stdout):
        """
        Function executes echo command
        :param stdin: input stream
        :param stdout: output stream
        :return: 0 - command was executed successfully
        """
        if len(self.args) != 0:
            print(*self.args, file=stdout, end='')
        else:
            print(stdin.read(), file=stdout, end='')
        return 0

    def __eq__(self, other):
        if isinstance(other, Echo):
            return self.args == other.args
        return False


class Wc(Command):
    """Class which represents wc command"""

    def __init__(self, args: List[str]):
        """
        Constructor
        :param args: list of command arguments
        :raise AttributeError if the length of the args list is greater than 1
        """
        if len(args) > 1:
            raise AttributeError("Too many arguments")
        self.arg = args[0] if len(args) > 0 else None

    def wc(self, lines):
        """
        Function that calculates count of lines, words and bytes
        :param lines: lines which represents data with text
        :return: total number of lines, words and bytes in the given lines
        """
        lines_cnt = 0
        words_cnt = 0
        bytes_cnt = 0
        for line in lines:
            lines_cnt += 1
            words_cnt += len(line.split())
            bytes_cnt += len(line.encode("utf-8"))
        return lines_cnt, words_cnt, bytes_cnt

    def wc_file(self, filename: str):
        """
        Function that calculates total number of lines, words and bytes in the given file
        :param filename: name of the file
        :raise FileNotFoundError if the given file cannot be found
        :return: None
        """
        try:
            with open(filename) as file:
                result = self.wc(file)
                print(*result, filename, file=self.stdout, end='')
        except FileNotFoundError:
            print(f'wc: {filename}: No such file or directory')

    def execute(self, stdin, stdout):
        """
        Function executes wc command
        :param stdin: input stream
        :param stdout: output stream
        :return: 0 - command was executed successfully
        """
        self.stdin = stdin
        self.stdout = stdout
        if not self.arg:
            print(*self.wc(self.stdin), file=self.stdout, end='')
        else:
            self.wc_file(self.arg)
        return 0

    def __eq__(self, other):
        if isinstance(other, Wc):
            return self.arg == other.arg
        return False


class Pwd(Command):
    """Class which represents pwd command"""

    def __init__(self, args):
        pass

    def execute(self, stdin, stdout):
        """
        Function executes pwd command
        :param stdin: input stream
        :param stdout: output stream
        :return:  0 - command was executed successfully
        """
        print(getcwd(), file=stdout, end='')
        return 0

    def __eq__(self, other):
        return isinstance(other, Pwd)


class Exit(Command):
    """Class which represents exit command"""

    def __init__(self, args):
        pass

    def execute(self, stdin, stdout):
        """
        Function executes exit command
        :param stdin: input stream
        :param stdout: output stream
        :raise SystemExit exception
        :return: 1 - process finished
        """
        return 1

    def __eq__(self, other):
        if isinstance(other, Exit):
            return True
        return False


class Declaration(Command):
    """Class which represents declaration command"""

    def __init__(self, args):
        """
        Constructor
        :param args: [dict of variables, name, value]
        :raise AttributeError if the length of the args list is not equals to 3
        """
        if len(args) != 3:
            raise AttributeError("Declaration class needs 3 arguments")
        self.dct = args[0]
        self.name = args[1]
        self.value = args[2]

    def execute(self, stdin, stdout):
        """
        Function executes declaration command
        :param stdin: input stream
        :param stdout: output stream
        :return: 0 - command was executed successfully
        """
        self.dct[self.name] = self.value
        return 0

    def __eq__(self, other):
        if isinstance(other, Declaration):
            return self.args == other.args
        return False


class External(Command):
    """Class which represents external command"""

    def __init__(self, args: List[str]):
        """
        Constructor
        :param args: list of command arguments
        :raise AttributeError if the length of the args list is equals zero
        """
        if len(args) < 2:
            raise AttributeError("External: command and vars expected")
        self.command = args[0]
        self.vars = args[1]
        self.args = args[2:]

    @staticmethod
    def decode(inp):
        try:
            return inp.decode(sys.stdout.encoding)
        except UnicodeDecodeError:
            return inp.decode('866')

    def execute(self, stdin, stdout):
        """
        Function executes external command
        :param stdin: input stream
        :param stdout: output stream
        :return return code
        """
        if isinstance(stdin, io.StringIO) or stdin.isatty():
            inp = stdin.read().encode()
        else:
            inp = b''
        env = os.environ.copy().update(self.vars)
        proc = sb.run(' '.join([self.command] + self.args), input=inp, stdout=sb.PIPE, stderr=sb.PIPE, env=env,
                      shell=True)
        if proc.returncode == 0:
            print(self.decode(proc.stdout.strip()), file=stdout, end='')
        else:
            print(self.decode(proc.stderr), end='')
        return False

    def __eq__(self, other):
        if isinstance(other, External):
            return self.args == other.args and self.vars == other.vars and self.command == other.command
        return False
