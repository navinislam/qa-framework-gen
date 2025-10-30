from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml

from framework.models.config import ProjectConfig


def load_yaml(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        return yaml.safe_load(stream) or {}


def load_project_config(path: str | Path) -> ProjectConfig:
    """Load a project configuration file into a ProjectConfig instance."""
    config_path = Path(path)
    if not config_path.is_file():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    data = load_yaml(config_path)
    return ProjectConfig.from_mapping(data)

