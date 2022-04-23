import io
from CLI.main import CLI


def test_double_different_quotes_1():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "x=10"
    cli.process(line, stdin, stdout)
    line = "echo "'$x'""
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "10\n"


def test_double_different_quotes_2():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "x=10"
    cli.process(line, stdin, stdout)
    line = "echo '\"$x\"'"
    print(line)
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "\"$x\"\n"


def test_single_quotes_1():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "x=10"
    cli.process(line, stdin, stdout)
    line = "echo '$x'=$x"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "$x = 10\n"


def test_single_quotes_2():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "echo '10 $x'"
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "10 $x\n"


def test_double_quotes():
    cli = CLI()
    stdin = io.StringIO()
    stdout = io.StringIO()
    line = "x=10"
    cli.process(line, stdin, stdout)
    line = 'echo "10 $x"'
    cli.process(line, stdin, stdout)
    stdout.seek(0, 0)
    result = stdout.read()
    assert result == "10 10\n"
