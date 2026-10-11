from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "Smart_College_Management_System.zip"
INCLUDE = [
    "campus", "smart_college", "templates", "static", "docs", "manage.py",
    "requirements.txt", "README.md", "setup.ps1", "start.ps1", "start.bat",
    "package.ps1", "package_project.py", ".env.example", "db.sqlite3",
]
SKIP = {".git", ".venv", "venv", "__pycache__", "media", "staticfiles"}

with ZipFile(ARCHIVE, "w", ZIP_DEFLATED) as bundle:
    for name in INCLUDE:
        path = ROOT / name
        if path.is_file():
            bundle.write(path, path.relative_to(ROOT))
        elif path.is_dir():
            for item in path.rglob("*"):
                relative = item.relative_to(ROOT)
                if item.is_file() and not any(part in SKIP for part in relative.parts) and item.suffix != ".pyc":
                    bundle.write(item, relative)

print(f"Created {ARCHIVE} ({ARCHIVE.stat().st_size:,} bytes)")
