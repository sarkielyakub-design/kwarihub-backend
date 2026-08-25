from pathlib import Path

from ..base import BaseGenerator


class ModuleGenerator(BaseGenerator):

    FILES = [
        "__init__.py",
        "models.py",
        "schemas.py",
        "repository.py",
        "service.py",
        "router.py",
        "validators.py",
        "permissions.py",
        "dependencies.py",
        "constants.py",
        "events.py",
        "exceptions.py",
    ]

    def generate(self, name: str):

        module = name.lower()

        class_name = module.capitalize()

        context = {
            "CLASS_NAME": class_name,
            "TABLE_NAME": module,
            "ROUTE": module,
        }

        folder = Path(
            "app/modules"
        ) / module

        self.engine.ensure_directory(folder)

        self.engine.ensure_directory(
            folder / "tests"
        )

        for file in self.FILES:

            target = folder / file

            if target.exists():
                continue

            if file == "__init__.py":
                target.write_text("")
                continue

            template = file.replace(
                ".py",
                ".tpl",
            )

            content = self.render(
                template,
                context,
            )

            self.write(
                str(target),
                content,
            )

        print(
            f"\n✅ Module '{module}' created successfully.\n"
        )