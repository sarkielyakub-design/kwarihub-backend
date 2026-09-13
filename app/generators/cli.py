import sys

from generators.module_generator import ModuleGenerator


class GeneratorCLI:

    def __init__(self):
        self.module_generator = ModuleGenerator()

    def run(self, argv):

        if len(argv) < 3:
            self.help()
            return

        command = argv[1].lower()
        name = argv[2]

        commands = {
            "module": self.module_generator.generate,
        }

        action = commands.get(command)

        if action is None:
            print(f"\n❌ Unknown command: {command}\n")
            self.help()
            return

        action(name)

    def help(self):

        print("""
=========================================
 KWARIHUB GENERATOR
=========================================

Usage:

python3 generate.py module users

Future Commands:

python3 generate.py model User
python3 generate.py schema User
python3 generate.py repository User
python3 generate.py service User
python3 generate.py router User
python3 generate.py migration User
python3 generate.py docs User

=========================================
""")