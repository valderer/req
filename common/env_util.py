import os
from pathlib import Path


def load_env_file(file_path: Path):
    """读取简单的 .env 文件，不覆盖系统中已经设置的变量。"""
    if not file_path.exists():
        return

    with file_path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())
