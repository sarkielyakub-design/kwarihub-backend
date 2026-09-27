import sys

from generators.cli import GeneratorCLI


def main():
    cli = GeneratorCLI()
    cli.run(sys.argv)


if __name__ == "__main__":
    main()