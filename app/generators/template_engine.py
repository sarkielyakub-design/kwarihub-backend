from pathlib import Path


class TemplateEngine:

    TEMPLATE_DIR = Path("generators/templates")

    @classmethod
    def render(cls, template_path: str, context: dict):

        file = cls.TEMPLATE_DIR / template_path

        if not file.exists():
            raise FileNotFoundError(
                f"Template not found: {template_path}"
            )

        content = file.read_text(encoding="utf-8")

        for key, value in context.items():

            content = content.replace(
                "{{" + key + "}}",
                str(value),
            )

        return content