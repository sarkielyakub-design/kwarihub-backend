from pathlib import Path

from generators.template_engine import TemplateEngine


class ModuleGenerator:

    def generate(self, module):

        module = module.lower()

        class_name = module.capitalize()

        folder = Path("app/modules") / module

        folder.mkdir(parents=True, exist_ok=True)

        (folder / "tests").mkdir(exist_ok=True)

        context = {
            "CLASS_NAME": class_name,
            "TABLE_NAME": module,
            "ROUTE": module,
        }

        files = {
            "__init__.py": "",
            "models.py": TemplateEngine.render(
                "module/model.tpl",
                context,
            ),
            "schemas.py": TemplateEngine.render(
                "module/schema.tpl",
                context,
            ),
            "repository.py": TemplateEngine.render(
                "module/repository.tpl",
                context,
            ),
            "service.py": TemplateEngine.render(
                "module/service.tpl",
                context,
            ),
            "router.py": TemplateEngine.render(
                "module/router.tpl",
                context,
            ),
            "validators.py": "",
            "permissions.py": "",
            "dependencies.py": "",
            "constants.py": "",
            "events.py": "",
            "exceptions.py": "",
        }

        for filename, content in files.items():

            path = folder / filename

            if not path.exists():
                path.write_text(
                    content,
                    encoding="utf-8",
                )

        print(f"\n✅ Module '{module}' generated successfully.\n")