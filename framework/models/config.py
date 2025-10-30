from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class ProjectConfig:
    """Configuration model for an automation project."""

    name: str
    base_url: str
    default_browser: str = "chrome"

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ProjectConfig":
        project_section = data.get("project")
        if not isinstance(project_section, Mapping):
            raise ValueError("Config must contain a 'project' mapping.")

        name = str(project_section.get("name", "automation-project"))
        base_url = str(project_section.get("base_url", "")).strip()
        if not base_url:
            raise ValueError("Project config requires a non-empty 'base_url'.")

        default_browser = str(
            project_section.get("default_browser", "chrome")
        ).lower()

        return cls(name=name, base_url=base_url, default_browser=default_browser)

