from pathlib import Path
from typing import Dict, Any


class GeneratorEngine:
    """
    Core engine responsible for:
    - Creating directories
    - Creating files
    - Writing templates
    - Rendering placeholders
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()

    def root(self) -> Path:
        return self.project_root

    def path(self, *parts) -> Path:
        return self.project_root.joinpath(*parts)

    def ensure_directory(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)

    def write_file(
        self,
        relative_path: str,
        content: str,
        overwrite: bool = False
    ):
        file_path = self.path(relative_path)

        self.ensure_directory(file_path.parent)

        if file_path.exists() and not overwrite:
            print(f"⚠ Skipped: {relative_path}")
            return

        file_path.write_text(
            content,
            encoding="utf-8"
        )

        print(f"✅ Created: {relative_path}")

    def read_template(self, template_path: str) -> str:

        file = self.path(
            "tools",
            "kwari_generator",
            "templates",
            template_path
        )

        if not file.exists():
            raise FileNotFoundError(
                f"Template not found: {template_path}"
            )

        return file.read_text(
            encoding="utf-8"
        )

    def render(
        self,
        template: str,
        context: Dict[str, Any]
    ) -> str:

        for key, value in context.items():
            template = template.replace(
                "{{" + key + "}}",
                str(value)
            )

        return template

    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any]
    ) -> str:

        template = self.read_template(
            template_name
        )

        return self.render(
            template,
            context
        )