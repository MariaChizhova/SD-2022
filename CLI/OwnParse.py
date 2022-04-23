import argparse


class OwnArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        raise ArgumentError(message)


class ArgumentError(Exception):
    pass
