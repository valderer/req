from pathlib import Path

import yaml


def load_yaml(file_path: Path):
    """读取 YAML 文件并返回 Python 字典或列表。"""
    with file_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)
