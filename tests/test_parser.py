from CLI.parser import Parser
from CLI.token_types import Type, Token
from CLI.commands import Cat, Echo, Wc, Pwd, Exit, External


def test_parse_cat():
    line = "cat main.py"
    parser = Parser(line, {})
    assert parser.parse() == [Cat(["main.py"])]


def test_parseCommands_cat():
    line = "cat main.py"
    parser = Parser(line, {})
    tokens = [Token("cat", Type.STRING), Token("main.py", Type.STRING), Token(chr(0), Type.END)]
    assert parser.parse_сommands(tokens) == [Cat(["main.py"])]


def test_parse_echo_one_argument():
    line = "echo 1"
    parser = Parser(line, {})
    assert parser.parse() == [Echo(["1"])]


def test_parse_echo_many_arguments():
    line = "echo 1 2 3"
    parser = Parser(line, {})
    assert parser.parse() == [Echo(["1", "2", "3"])]


def test_parseCommands_echo_one_argument():
    line = "echo Hello"
    parser = Parser(line, {})
    tokens = [Token("echo", Type.STRING), Token("Hello", Type.STRING), Token(chr(0), Type.END)]
    assert parser.parse_сommands(tokens) == [Echo(["Hello"])]


def test_parseCommands_echo_many_arguments():
    line = "echo Hello world"
    parser = Parser(line, {})
    tokens = [Token("echo", Type.STRING), Token("Hello", Type.STRING), Token("world", Type.STRING),
              Token(chr(0), Type.END)]
    assert parser.parse_сommands(tokens) == [Echo(["Hello", "world"])]


def test_parce_wc():
    line = "wc file.txt"
    parser = Parser(line, {})
    assert parser.parse() == [Wc(["file.txt"])]


def test_parseCommands_wc_file():
    line = "wc file.txt"
    parser = Parser(line, {})
    tokens = [Token("wc", Type.STRING), Token("main.py", Type.STRING), Token(chr(0), Type.END)]
    assert parser.parse_сommands(tokens) == [Wc(["main.py"])]


def test_parse_pwd():
    line = "pwd"
    parser = Parser(line, {})
    assert parser.parse() == [Pwd([])]


def test_parseCommands_pwd():
    line = "pwd"
    parser = Parser(line, {})
    tokens = [Token("pwd", Type.STRING), Token(chr(0), Type.END)]
    assert parser.parse_сommands(tokens) == [Pwd([])]


def test_parse_exit():
    line = "exit"
    parser = Parser(line, {})
    assert parser.parse() == [Exit([])]


def test_parseCommands_exit():
    line = "exit"
    parser = Parser(line, {})
    tokens = [Token("exit", Type.STRING), Token(chr(0), Type.END)]
    assert parser.parse_сommands(tokens) == [Exit([])]


def test_parse_external():
    line = "git init"
    parser = Parser(line, {})
    assert parser.parse() == [External(["git", {}, "init"])]


def test_parseCommands_external():
    line = "git init"
    parser = Parser(line, {})
    tokens = [Token("git", Type.STRING), Token("init", Type.STRING), Token(chr(0), Type.END)]
    assert parser.parse_сommands(tokens) == [External(["git", {}, "init"])]


def test_parse_quotes_echo_one_word():
    line = "echo 'Hello'"
    parser = Parser(line, {})
    assert parser.parse() == [Echo(["Hello"])]


def test_parse_quotes_echo_many_words():
    line = "echo 'Hello world!'"
    parser = Parser(line, {})
    assert parser.parse() == [Echo(["Hello world!"])]


def test_parse_quotes():
    line = 'cat "file.txt"'
    parser = Parser(line, {})
    assert parser.parse() == [Cat(["file.txt"])]


def test_token_methods():
    token = Token("echo", Type.STRING)
    assert token.getValue() == "echo"
    assert token.getType() == Type.STRING


def test_parseCommands_pipes_echo_wc():
    line = "echo Hello | exit | echo Hi"
    parser = Parser(line, {})
    tokens = [Token("echo", Type.STRING), Token("Hello", Type.STRING), Token("|", Type.PIPE),
              Token("exit", Type.STRING), Token("|", Type.PIPE), Token("echo", Type.STRING), Token("Hi", Type.STRING),
              Token(chr(0), Type.END)]
    assert parser.parse_сommands(tokens) == [Echo(["Hello"]), Exit([]), Echo(["Hi"])]
