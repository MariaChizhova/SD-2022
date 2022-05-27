import io
import re
import os
from abc import ABC, abstractmethod
from os import getcwd, listdir, chdir
from typing import List
import sys
import subprocess as sb
from CLI.OwnParse import OwnArgumentParser, ArgumentError


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


class Grep(Command):
    """Class which represents grep command"""

    def __init__(self, args: List[str]):
        """
        Constructor
        :param args: list of command arguments
        :raise AttributeError if the length of the args list is equals zero
        """
        if len(args) == 0:
            raise AttributeError("External: command and vars expected")
        self.parser = OwnArgumentParser()
        self.parser.add_argument('needle', type=str)
        self.parser.add_argument('files', nargs='*', type=str)
        self.parser.add_argument('-w', dest='word_regexp', action='store_true')
        self.parser.add_argument('-i', dest='ignore_case', action='store_true')
        self.parser.add_argument('-A', dest='after_context', default=0)
        self.args = args

    @staticmethod
    def join_ranges(ranges: List[List[int]]) -> List[List[int]]:
        """
        Merges intervals that intersect
        :param ranges: Intervals
        :return: Interval without crossing
        """
        ranges.sort()
        first, count = 0, 0
        new_ranges = []
        for element in ranges:
            count = count + 1 if element[1] == 0 else count - 1
            if count == 1 and element[1] == 0:
                first = element[0]
            if count == 0 and element[1] == 1:
                new_ranges.append([first, element[0]])
        return new_ranges

    def calculate_result(self, file_name, count_files, lines) -> List[str]:
        """
        Looking for matches in lines
        :param file_name: File name
        :param count_files: Number of files
        :param lines: Lines
        :return: Lines that match
        """
        result = []
        self.args.needle = self.args.needle.lower() if self.args.ignore_case else self.args.needle
        self.args.needle = r'(^|\W)' + self.args.needle + r'(\W|$)' if self.args.word_regexp else self.args.needle
        ranges = []
        for i, line in enumerate(lines):
            line = line.lower() if self.args.ignore_case else line
            if re.search(self.args.needle, line):
                ranges.append([i, 0])
                ranges.append([self.args.after_context + i + 1, 1])
        for i in self.join_ranges(ranges):
            result += lines[i[0]:i[1]]
        if count_files > 1:
            result = [f'{file_name}:{line}' for line in result]
        return result

    def print_grep(self, in_file, count_files, file):
        """
        Processes the data source and print the result
        :param in_file: Data source
        :param count_files: Number of files
        :param file: File name
        """
        lines = [line.rstrip('\n') for line in in_file]
        result = '\n'.join(self.calculate_result(file, count_files, lines))
        print(result, file=self.stdout, end='')

    def execute(self, stdin, stdout):
        """
        Function executes grep command
        :param stdin: input stream
        :param stdout: output stream
        :return: return code
        """
        try:
            self.args = self.parser.parse_args(self.args)
        except ArgumentError as e:
            print(*e.args)
            return False
        try:
            self.args.after_context = int(self.args.after_context)
            if self.args.after_context < 0:
                raise ValueError
        except ValueError:
            print('ValueError: the value following -A is not correct')
            return False
        self.stdout = stdout
        if not self.args.files:
            self.print_grep(stdin.readlines(), 0, '')
        else:
            for file in self.args.files:
                try:
                    with open(file, 'r', encoding="utf-8") as in_file:
                        self.print_grep(in_file.readlines(), len(self.args.files), file)
                except FileNotFoundError:
                    print(f"No such file or directory: {file}")
                    return False
        return False


class Cd(Command):
    """Class which represents cd command"""

    def __init__(self, args: List[str]):
        self.args = args

    def execute(self, stdin, stdout):
        """
        Function executes cd command to change current directory to directory self.args[0]
        If there are no arguments, cd command changes current directory to directory sys.path[0]
        :param stdin: input stream
        :param stdout: output stream
        :return:  0 - command was executed successfully
        """
        if len(self.args) > 1:
            print("Error: Too many arguments", file=stdout)
            return 0

        dir_name = os.path.expanduser('~') if len(self.args) == 0 else os.path.join(os.path.abspath(getcwd()), self.args[0])

        if os.path.isfile(dir_name):
            print(f"cd: not a directory: {self.args[0]}", file=stdout)
            return 0

        if not os.path.exists(dir_name):
            print(f"No such file or directory: {dir_name}", file=stdout)
            return 0

        chdir(dir_name)
        return 0


class Ls(Command):
    """Class which represents ls command to list contents of a directory, for example folder and file names"""

    def __init__(self, args: List[str]):
        self.args = args

    def execute(self, stdin, stdout):
        """
        Function executes ls command
        :param stdin: input stream
        :param stdout: output stream
        :return:  0 - command was executed successfully
        """

        if len(self.args) == 0:
            self.args.append("")

        for relative_path in self.args:
            dir_name = os.path.join(os.path.abspath(getcwd()), relative_path)
            if not os.path.exists(dir_name):
                print(f"No such file or directory: {dir_name}", file=stdout)
                print(file=stdout)
                continue

            if len(self.args) > 1:
                print(f"{relative_path}:", file=stdout)

            if os.path.isfile(dir_name):
                print(relative_path, file=stdout)
                continue

            for file_name in listdir(dir_name):
                print(file_name, file=stdout)

            print(file=stdout)

        return 0
