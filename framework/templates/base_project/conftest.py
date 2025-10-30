from __future__ import annotations

import os
from pathlib import Path

import pytest

from framework import ProjectConfig, SeleniumBasePage, load_project_config

pytest_plugins = [
    "framework.fixtures.selenium_fixtures",
    "framework.fixtures.common_fixtures",
]

PROJECT_ROOT = Path(__file__).parent


@pytest.fixture(scope="session")
def project_config() -> ProjectConfig:
    config = load_project_config(PROJECT_ROOT / "config.yml")
    os.environ.setdefault("BROWSER", config.default_browser)
    os.environ.setdefault("URI", config.base_url)
    return config


@pytest.fixture(scope="session")
def base_url(project_config: ProjectConfig) -> str:
    return project_config.base_url


@pytest.fixture
def base_page(base_factory: SeleniumBasePage, base_url: str) -> SeleniumBasePage:
    """Expose a selenium base page instance for tests."""
    base_factory.open(base_url)
    return base_factory
