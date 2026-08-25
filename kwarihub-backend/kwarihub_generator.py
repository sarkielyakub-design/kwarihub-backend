from pathlib import Path

PROJECT_NAME = "KWARIHUB"

modules = [
    "auth",
    "users",
    "roles",
    "vendors",
    "shops",
    "categories",
    "products",
    "inventory",
    "cart",
    "wishlist",
    "orders",
    "payments",
    "wallet",
    "reviews",
    "notifications",
    "support",
    "search",
    "dashboard",
    "reports",
    "analytics",
    "settings",
    "banners",
]

module_files = [
    "__init__.py",
    "router.py",
    "service.py",
    "repository.py",
    "models.py",
    "schemas.py",
    "dependencies.py",
    "constants.py",
    "exceptions.py",
]

base_dirs = [
    "app",
    "app/core",
    "app/database",
    "app/common",
    "app/utils",
    "app/security",
    "app/middleware",
    "app/modules",
    "app/tests",
    "app/static",
    "app/uploads",
    "app/logs",
]

base_files = {
    "app/main.py": "",
    "app/core/config.py": "",
    "app/core/security.py": "",
    "app/database/base.py": "",
    "app/database/session.py": "",
    ".env": "",
    ".env.example": "",
    "requirements.txt": "",
    "README.md": f"# {PROJECT_NAME}\n",
}

print("Creating directories...")

for folder in base_dirs:
    Path(folder).mkdir(parents=True, exist_ok=True)

print("Creating modules...")

for module in modules:
    module_path = Path("app/modules") / module
    module_path.mkdir(parents=True, exist_ok=True)

    for file in module_files:
        filepath = module_path / file

        if not filepath.exists():
            filepath.write_text(
                f'"""{PROJECT_NAME} - {module} - {file}"""\n',
                encoding="utf-8",
            )

print("Creating base files...")

for file, content in base_files.items():
    path = Path(file)

    if not path.exists():
        path.write_text(content, encoding="utf-8")

print("\n✅ Project Generated Successfully!")
print(f"📦 Modules Created: {len(modules)}")
print(f"📄 Files Per Module: {len(module_files)}")
print(f"📁 Total Module Files: {len(modules) * len(module_files)}")