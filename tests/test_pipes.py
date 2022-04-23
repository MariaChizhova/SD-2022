from CLI.commands import Cat, Echo, Wc
from CLI.main import CLI
import io
from CLI.parser import Parser
from CLI.token_types import Token, Type


def test_execute_pipes_echo_cat():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "echo Hello | cat"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "Hello\n"


def test_parse_pipes_echo_cat():
    line = "echo Hello | cat"
    parser = Parser(line, {})
    assert parser.parse() == [Echo(["Hello"]), Cat([])]


def test_parseCommands_pipes_echo_wc():
    line = "echo Hello | wc"
    parser = Parser(line, {})
    tokens = [Token("echo", Type.STRING), Token("Hello", Type.STRING), Token("|", Type.PIPE), Token("wc", Type.STRING),
              Token(chr(0), Type.END)]
    assert parser.parse_commands(tokens) == [Echo(["Hello"]), Wc([])]


def test_execute_pipes_with_exit_middle():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    assert cli.is_running
    line = "echo Hello | exit | echo world"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "world\n"
    assert cli.is_running


def test_execute_pipes_exit_end():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    assert cli.is_running
    line = "x=1 | echo $x | exit"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == ""
    assert cli.is_running


def test_execute_pipes_with_vars1():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "x=1 | echo $x"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == ""


def test_execute_pipes_with_vars2():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "echo Hello | x='Hello' | echo $x"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == ""


def test_execute_pipes_with_vars3():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "echo 'Hello' | wc | x=1 | y=1 | echo $x"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == ""


def test_execute_pipes_echo_external1():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "echo 'Hello' | grep 'buy'"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == ""


def test_execute_pipes_echo_external2():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "echo 'Hello' | grep 'Hel'"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "Hello\n"


def test_execute_pipes_one_empty():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "echo Hello |"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "Hello\n"


def test_execute_pipes_two_empty():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "echo Hello | |"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "Hello\n"
