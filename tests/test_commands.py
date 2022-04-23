import io
import os

from CLI.main import CLI


def test_execute_cat():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "cat tests/file.txt"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "Hello world!\n"


def test_execute_echo():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "echo Hello"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "Hello\n"


def test_execute_wc():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "wc tests/file.txt"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "1 2 12 tests/file.txt\n"


def test_execute_pwd():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "pwd"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == os.getcwd() + '\n'


def test_execute_exit():
    cli = CLI()
    assert cli.is_running
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "exit"
    cli.process(line, stdin, stdout)
    assert not cli.is_running


def test_execute_external():
    if os.name == 'nt':
        cli = CLI()
        stdin = io.StringIO()
        stdout = io.StringIO()
        assert not os.path.exists('./external.txt')
        line = "copy /b NUL external.txt"
        cli.process(line, stdin, stdout)
        assert os.path.exists('external.txt')
        line = "del external.txt"
        cli.process(line, stdin, stdout)
        assert not os.path.exists('external.txt')
    elif os.name == 'posix':
        cli = CLI()
        stdin = io.StringIO()
        stdout = io.StringIO()
        assert not os.path.exists('./external.txt')
        line = "touch ./external.txt"
        cli.process(line, stdin, stdout)
        assert os.path.exists('./external.txt')
        line = "rm ./external.txt"
        cli.process(line, stdin, stdout)
        assert not os.path.exists('./external.txt')


def test_declaration():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "x=5"
    cli.process(line, stdin, stdout)
    line = "echo $x"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "5\n"


def test_declaration_twice():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "x=5"
    cli.process(line, stdin, stdout)
    line = "x=10"
    cli.process(line, stdin, stdout)
    line = "echo $x"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "10\n"


def test_grep_w_NotEmpty():
    cli = CLI()
    stdin = io.StringIO("Hello world\nLondon is the capital of Great Britain")
    stdout = io.StringIO()
    line = "grep -w 'Hello world'"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "Hello world\n"


def test_grep_w_Empty():
    cli = CLI()
    stdin = io.StringIO("Hello world\nLondon is the capital of Great Britain")
    stdout = io.StringIO()
    line = "grep -w 'Minsk is the capital of Belarus'"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == ""


def test_grep_i():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "echo Hello | grep -i hElLo"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "Hello\n"


def test_grep_A_0():
    cli = CLI()
    stdin = io.StringIO("pref needle?\nneedle? suf\nthe needl\npref needle? suf")
    stdout = io.StringIO()
    line = "grep -A 0 suf"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "needle? suf\npref needle? suf\n"


def test_grep_A_1():
    cli = CLI()
    stdin = io.StringIO("pref needle?\nneedle? suf\nthe needl\npref needle? suf")
    stdout = io.StringIO()
    line = "grep -A 1 'the'"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "the needl\npref needle? suf\n"


def test_grep_A_3():
    cli = CLI()
    stdin = io.StringIO("pref needle?\nneedle? suf\nthe needl\npref needle? suf")
    stdout = io.StringIO()
    line = "grep -A 3 'pref'"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "pref needle?\nneedle? suf\nthe needl\npref needle? suf\n"


def test_grep_A_with_intersection():
    cli = CLI()
    stdin = io.StringIO("Hello world\nthe world hey\nbuy\nokay")
    stdout = io.StringIO()
    line = "grep -A 1 'world'"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "Hello world\nthe world hey\nbuy\n"


def test_grep_file_extension():
    cli = CLI()
    stdin = io.StringIO("parser.cpp\ntext.txt\nmain.py")
    stdout = io.StringIO()
    line = "grep '.txt'"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "text.txt\n"


def test_grep_E():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "echo 'ioT\niOT\nIot\nIOT' | grep '[iI][oO]t'"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "Iot\n"


def test_grep_E_start_with():
    cli = CLI()
    stdin = io.StringIO(
        "Halfway down the stairs\nIs a stair\nWhere I sit.\nThere isn't any\nOther stair\nQuite like\nIt.")
    stdout = io.StringIO()
    line = "grep '^Where'"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "Where I sit.\n"


def test_grep_E_ends_with():
    cli = CLI()
    stdin = io.StringIO(
        "Halfway down the stairs\nIs a stair\nWhere I sit.\nThere isn't any\nOther stair\nQuite like\nIt.")
    stdout = io.StringIO()
    line = "grep 'stair$'"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "Is a stair\nOther stair\n"


def test_grep_E_with_star():
    cli = CLI()
    stdin = io.StringIO("yellow\nyeeellow\nyeyelo")
    stdout = io.StringIO()
    line = "grep 'y*llow'"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "yellow\nyeeellow\n"


def test_grep_combine_keys1():
    cli = CLI()
    stdin = io.StringIO(
        "Halfway down the stairs\nIs a stair\nWhere I sit.\nThere isn't any\nOther stair\nQuite like\nIt.")
    stdout = io.StringIO()
    line = "grep -A 1 'Where'"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "Where I sit.\nThere isn't any\n"


def test_grep_combine_keys2():
    cli = CLI()
    stdin = io.StringIO(
        "Halfway down the stairs\nIs a stair\nWhere I sit.\nThere isn't any\nOther stair\nQuite like\nIt.")
    stdout = io.StringIO()
    line = "grep -iw 'oTheR'"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "Other stair\n"
