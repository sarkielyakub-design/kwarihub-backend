from pathlib import Path

PROJECT_STRUCTURE = {
    "generators": {
        "__init__.py": "",
        "cli.py": "",
        "config.py": "",
        "utils.py": "",
        "module_generator.py": "",
        "model_generator.py": "",
        "schema_generator.py": "",
        "repository_generator.py": "",
        "service_generator.py": "",
        "router_generator.py": "",
        "docs_generator.py": "",
        "upload_generator.py": "",
        "migration_generator.py": "",
        "templates": {
            "module": {},
            "model": {},
            "schema": {},
            "repository": {},
            "service": {},
            "router": {},
            "docs": {},
            "tests": {}
        }
    },

    "storage": {
        "uploads": {
            "avatars": {},
            "vendors": {},
            "products": {},
            "shops": {},
            "brands": {},
            "categories": {},
            "documents": {},
            "logos": {},
            "banners": {}
        }
    },

    "docs": {
        "api": {},
        "swagger": {},
        "postman": {}
    },

    "tests": {},

    "generate.py": '''"""
KWARIHUB Generator

This file will become the CLI entry point.
Implemented in Part 2.
"""

print("KWARIHUB Generator is ready.")
''',

    "README_GENERATOR.md": """# KWARIHUB Generator

Automatically generates:

- Modules
- Models
- Schemas
- Services
- Repositories
- Routers
- Documentation
- Upload folders
- Alembic migrations

Version: 1.0
"""
}


def create_structure(base_path: Path, structure: dict):
    for name, content in structure.items():

        path = base_path / name

        if isinstance(content, dict):

            path.mkdir(parents=True, exist_ok=True)
            create_structure(path, content)

        else:

            path.parent.mkdir(parents=True, exist_ok=True)

            if not path.exists():
                path.write_text(content, encoding="utf-8")
                print(f"Created: {path}")

            else:
                print(f"Exists : {path}")


def main():

    print("=" * 60)
    print("      KWARIHUB GENERATOR BOOTSTRAPPER")
    print("=" * 60)

    create_structure(Path("."), PROJECT_STRUCTURE)

    print()
    print("=" * 60)
    print("Framework created successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()