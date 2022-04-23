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
    assert result == "\n5\n"
