"""
Command-line interface for qa-framework-gen.
"""

from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path
from typing import Any

import click
import questionary
import yaml
from jinja2 import Environment, Template


def _slugify(value: str) -> str:
    """Convert a string to a URL-safe slug."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return slug or "project"


def _package_name(value: str) -> str:
    """Convert a string to a Python package name."""
    return _slugify(value).replace("-", "_")


def _class_name(value: str) -> str:
    """Convert a string to a Python class name for page objects."""
    tokens = re.split(r"[^a-zA-Z0-9]+", value)
    name = "".join(token.capitalize() for token in tokens if token)
    if not name:
        name = "Page"
    if not name.endswith("Page"):
        name = f"{name}Page"
    return name


def _load_config(project_root: Path) -> dict[str, Any] | None:
    """Load .framework-config.yml from project root."""
    config_path = project_root / ".framework-config.yml"
    if not config_path.exists():
        return None

    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def _generate_config(context: dict[str, Any], output_path: Path) -> None:
    """Generate .framework-config.yml file."""
    config = {
        "framework": {
            "version": "1.0.0",
            "generator": "qa-framework-gen",
            "created": datetime.datetime.now().isoformat(),
        },
        "project": {
            "name": context["project_name"],
            "base_url": context["base_url"],
        },
        "driver": {
            "type": context["driver_type"],
            "browsers": context.get("browsers", ["chrome"]),
        },
        "features": {
            "docker": context.get("docker", False),
            "ci_cd": context.get("ci_cd", False),
            "allure": context.get("allure", False),
            "quality_tools": context.get("quality_tools", False),
            "pre_commit": context.get("pre_commit", False),
            "parallel": context.get("parallel", False),
            "flaky_retry": context.get("flaky_retry", False),
            "api_testing": context.get("api_testing", False),
        },
        "settings": {
            "logging_mode": "json",
            "test_data_format": "yaml",
            "playwright_async": context.get("playwright_async", True),
        },
    }

    with open(output_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


@click.group()
@click.version_option(version="0.1.0", prog_name="qfg")
def cli() -> None:
    """QA Framework Generator - Create pytest automation frameworks with ease."""
    pass


@cli.command()
@click.option(
    "--name",
    prompt="Project name",
    help="Name of the project to create",
)
@click.option(
    "--base-url",
    prompt="Base URL",
    default="https://www.saucedemo.com",
    help="Base URL for the application under test",
)
@click.option(
    "-d",
    "--directory",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path("."),
    help="Directory where the project will be created",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Overwrite existing directory if not empty",
)
def init(name: str, base_url: str, directory: Path, force: bool) -> None:
    """Initialize a new automation framework project."""

    # Interactive prompts for configuration
    click.echo("\n🎯 QA Framework Generator\n")

    # Driver selection
    driver_choice = questionary.select(
        "Which driver(s) do you want to use?",
        choices=[
            "Selenium WebDriver",
            "Playwright",
            "Both (Selenium + Playwright)",
        ],
    ).ask()

    driver_map = {
        "Selenium WebDriver": "selenium",
        "Playwright": "playwright",
        "Both (Selenium + Playwright)": "both",
    }
    driver_type = driver_map[driver_choice]

    # Browser selection
    if driver_type in ["selenium", "both"]:
        browsers = questionary.checkbox(
            "Select browsers to support:",
            choices=["chrome", "firefox", "edge"],
            default=["chrome"],
        ).ask()
    else:
        browsers = ["chromium", "firefox", "webkit"]

    # Feature selection
    features = questionary.checkbox(
        "Select features to include:",
        choices=[
            questionary.Choice("Docker Compose (Selenium Grid)", value="docker", checked=True),
            questionary.Choice("CI/CD (GitHub Actions)", value="ci_cd", checked=True),
            questionary.Choice("Allure Reporting", value="allure", checked=True),
            questionary.Choice("Quality Tools (black, flake8, mypy, bandit)", value="quality_tools", checked=True),
            questionary.Choice("Pre-commit Hooks", value="pre_commit", checked=True),
            questionary.Choice("Parallel Execution (pytest-xdist)", value="parallel", checked=True),
            questionary.Choice("Flaky Test Retry", value="flaky_retry", checked=False),
            questionary.Choice("API Testing Support (requests)", value="api_testing", checked=False),
        ],
    ).ask()

    # Create context for template rendering
    project_slug = _slugify(name)
    target_dir = directory / project_slug

    # Check if directory exists
    if target_dir.exists() and not force:
        if any(target_dir.iterdir()):
            click.echo(f"❌ Directory '{target_dir}' already exists and is not empty. Use --force to overwrite.")
            sys.exit(1)

    target_dir.mkdir(parents=True, exist_ok=True)

    context = {
        "project_name": name,
        "project_slug": project_slug,
        "project_package": _package_name(name),
        "base_url": base_url.rstrip("/"),
        "driver_type": driver_type,
        "browsers": browsers,
        **{feature: True for feature in features},
    }

    # Generate .framework-config.yml
    _generate_config(context, target_dir / ".framework-config.yml")

    # Generate project files
    click.echo(f"\n📦 Creating project structure in {target_dir}...")

    # Create directory structure based on driver type
    if driver_type == "selenium":
        (target_dir / "pages").mkdir(exist_ok=True)
        (target_dir / "tests").mkdir(exist_ok=True)
    elif driver_type == "playwright":
        (target_dir / "pages_pw").mkdir(exist_ok=True)
        (target_dir / "tests_pw").mkdir(exist_ok=True)
    else:  # both
        (target_dir / "pages").mkdir(exist_ok=True)
        (target_dir / "tests").mkdir(exist_ok=True)
        (target_dir / "pages_pw").mkdir(exist_ok=True)
        (target_dir / "tests_pw").mkdir(exist_ok=True)

    (target_dir / "tests" / "data").mkdir(parents=True, exist_ok=True)

    # Create __init__.py files
    for pages_dir in ["pages", "pages_pw"]:
        if (target_dir / pages_dir).exists():
            (target_dir / pages_dir / "__init__.py").write_text("")

    for tests_dir in ["tests", "tests_pw"]:
        if (target_dir / tests_dir).exists():
            (target_dir / tests_dir / "__init__.py").write_text("")

    # Generate pytest.ini
    pytest_ini_content = f"""[pytest]
addopts = -v --strict-markers --tb=short
testpaths = tests{' tests_pw' if driver_type == 'both' else ''}
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    smoke: Smoke tests (critical path)
    regression: Regression test suite
    critical: Critical functionality tests
    selenium: Selenium WebDriver tests
    playwright: Playwright tests
    ui: UI layer tests
    api: API layer tests
"""
    (target_dir / "pytest.ini").write_text(pytest_ini_content)

    # Generate requirements.txt
    requirements = [
        "pytest>=7.4,<9",
    ]

    if driver_type in ["selenium", "both"]:
        requirements.extend([
            "selenium>=4.14,<5",
        ])

    if driver_type in ["playwright", "both"]:
        requirements.extend([
            "playwright>=1.41,<2",
            "pytest-playwright>=0.4.4,<0.5",
        ])

    if "allure" in features:
        requirements.append("allure-pytest>=2.13,<3")

    if "parallel" in features:
        requirements.append("pytest-xdist>=3.3,<4")

    if "flaky_retry" in features:
        requirements.append("pytest-retry>=1.5,<2")

    if "api_testing" in features:
        requirements.append("requests>=2.31,<3")

    requirements.extend([
        "structlog>=23.1,<25",
        "pyyaml>=6.0,<7",
    ])

    (target_dir / "requirements.txt").write_text("\n".join(sorted(requirements)) + "\n")

    # Generate README.md
    readme_content = f"""# {name}

Automation testing framework generated with qa-framework-gen.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (if using Playwright)
playwright install
```

## Running Tests

```bash
# Run all tests
pytest

# Run with parallel execution
pytest -n auto

# Run specific marker
pytest -m smoke
```

## Configuration

Project configuration is stored in `.framework-config.yml`.

Base URL: {base_url}
Driver: {driver_type}
"""
    (target_dir / "README.md").write_text(readme_content)

    # Generate .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv

# Testing
.pytest_cache/
.coverage
htmlcov/
*.html
allure-results/
allure-report/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
"""
    (target_dir / ".gitignore").write_text(gitignore_content)

    click.echo(f"✅ Project '{name}' created successfully!")
    click.echo(f"\n📂 Project location: {target_dir}")
    click.echo(f"\n🚀 Next steps:")
    click.echo(f"   cd {project_slug}")
    click.echo(f"   pip install -r requirements.txt")
    if driver_type in ["playwright", "both"]:
        click.echo(f"   playwright install")
    click.echo(f"   qfg add-page login")
    click.echo(f"   qfg add-test login")


@cli.command()
@click.argument("page_name")
@click.option(
    "--url",
    help="URL path for the page (e.g., /login)",
)
@click.option(
    "--driver",
    type=click.Choice(["selenium", "playwright", "both"]),
    help="Driver type (reads from config if not specified)",
)
def add_page(page_name: str, url: str | None, driver: str | None) -> None:
    """Add a new page object to the project."""

    # Load config
    project_root = Path.cwd()
    config = _load_config(project_root)

    if not config:
        click.echo("❌ Could not find .framework-config.yml. Run this command from a generated project directory.")
        sys.exit(1)

    # Determine driver type
    config_driver = config["driver"]["type"]

    if driver is None:
        if config_driver == "both":
            driver = questionary.select(
                "Which driver should this page object target?",
                choices=["Selenium", "Playwright", "Both"],
            ).ask().lower()
        else:
            driver = config_driver

    # Determine URL
    base_url = config["project"]["base_url"]
    if url is None:
        url = questionary.text(
            "Page URL path (e.g., /login):",
            default="/",
        ).ask()

    full_url = f"{base_url}{url}" if url.startswith("/") else url

    # Generate page objects
    class_name = _class_name(page_name)
    module_slug = _slugify(page_name).replace("-", "_")

    if driver in ["selenium", "both"]:
        pages_dir = project_root / "pages"
        _create_selenium_page(pages_dir, module_slug, class_name, page_name, full_url)
        click.echo(f"✅ Created Selenium page object: pages/{module_slug}_page.py")

    if driver in ["playwright", "both"]:
        pages_dir = project_root / "pages_pw"
        _create_playwright_page(pages_dir, module_slug, class_name, page_name, full_url)
        click.echo(f"✅ Created Playwright page object: pages_pw/{module_slug}_page.py")


@cli.command()
@click.argument("test_name")
@click.option(
    "--type",
    "test_type",
    type=click.Choice(["ui", "api"]),
    help="Test type (ui or api)",
)
@click.option(
    "--driver",
    type=click.Choice(["selenium", "playwright", "both"]),
    help="Driver type for UI tests",
)
def add_test(test_name: str, test_type: str | None, driver: str | None) -> None:
    """Add a new test file to the project."""

    # Load config
    project_root = Path.cwd()
    config = _load_config(project_root)

    if not config:
        click.echo("❌ Could not find .framework-config.yml. Run this command from a generated project directory.")
        sys.exit(1)

    # Determine test type
    api_enabled = config["features"].get("api_testing", False)
    if test_type is None:
        choices = ["UI"]
        if api_enabled:
            choices.append("API")

        test_type = questionary.select(
            "What type of test?",
            choices=choices,
        ).ask().lower()

    if test_type == "api" and not api_enabled:
        click.echo("❌ API testing is not enabled in this project. Re-run 'qfg init' with API testing enabled.")
        sys.exit(1)

    # For UI tests, determine driver
    if test_type == "ui":
        config_driver = config["driver"]["type"]

        if driver is None:
            if config_driver == "both":
                driver = questionary.select(
                    "Which driver should this test use?",
                    choices=["Selenium", "Playwright", "Both"],
                ).ask().lower()
            else:
                driver = config_driver

        module_slug = _slugify(test_name).replace("-", "_")

        if driver in ["selenium", "both"]:
            tests_dir = project_root / "tests"
            _create_selenium_test(tests_dir, module_slug, test_name)
            click.echo(f"✅ Created Selenium test: tests/test_{module_slug}.py")

        if driver in ["playwright", "both"]:
            tests_dir = project_root / "tests_pw"
            _create_playwright_test(tests_dir, module_slug, test_name)
            click.echo(f"✅ Created Playwright test: tests_pw/test_{module_slug}_pw.py")
    else:
        # API test
        module_slug = _slugify(test_name).replace("-", "_")
        tests_dir = project_root / "tests"
        _create_api_test(tests_dir, module_slug, test_name, config["project"]["base_url"])
        click.echo(f"✅ Created API test: tests/test_{module_slug}_api.py")


def _create_selenium_page(pages_dir: Path, module_slug: str, class_name: str, display_name: str, url: str) -> None:
    """Create a Selenium page object file."""
    content = f'''"""Page object for {display_name}."""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver


class {class_name}:
    """Page object for {display_name} page."""

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.url = "{url}"

    def visit(self) -> None:
        """Navigate to the page."""
        self.driver.get(self.url)
'''

    target_file = pages_dir / f"{module_slug}_page.py"
    target_file.write_text(content)

    # Update __init__.py
    init_file = pages_dir / "__init__.py"
    import_line = f"from .{module_slug}_page import {class_name}\n"
    if init_file.exists():
        existing = init_file.read_text()
        if import_line.strip() not in existing:
            init_file.write_text(existing + import_line)
    else:
        init_file.write_text(import_line)


def _create_playwright_page(pages_dir: Path, module_slug: str, class_name: str, display_name: str, url: str) -> None:
    """Create a Playwright page object file."""
    content = f'''"""Page object for {display_name}."""

from playwright.async_api import Page


class {class_name}:
    """Page object for {display_name} page."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.url = "{url}"

    async def visit(self) -> None:
        """Navigate to the page."""
        await self.page.goto(self.url)
'''

    target_file = pages_dir / f"{module_slug}_page.py"
    target_file.write_text(content)

    # Update __init__.py
    init_file = pages_dir / "__init__.py"
    import_line = f"from .{module_slug}_page import {class_name}\n"
    if init_file.exists():
        existing = init_file.read_text()
        if import_line.strip() not in existing:
            init_file.write_text(existing + import_line)
    else:
        init_file.write_text(import_line)


def _create_selenium_test(tests_dir: Path, module_slug: str, test_name: str) -> None:
    """Create a Selenium test file."""
    class_name = _class_name(test_name)
    content = f'''"""Tests for {test_name}."""

import pytest
from selenium.webdriver.remote.webdriver import WebDriver


@pytest.mark.selenium
@pytest.mark.ui
class Test{class_name.replace("Page", "")}:
    """Test suite for {test_name}."""

    def test_example(self, driver: WebDriver) -> None:
        """Example test - replace with actual test logic."""
        assert True, "Replace with actual test"
'''

    target_file = tests_dir / f"test_{module_slug}.py"
    target_file.write_text(content)


def _create_playwright_test(tests_dir: Path, module_slug: str, test_name: str) -> None:
    """Create a Playwright test file."""
    class_name = _class_name(test_name)
    content = f'''"""Tests for {test_name} (Playwright)."""

import pytest
from playwright.async_api import Page


@pytest.mark.playwright
@pytest.mark.ui
@pytest.mark.asyncio
class Test{class_name.replace("Page", "")}Playwright:
    """Playwright test suite for {test_name}."""

    async def test_example(self, page: Page) -> None:
        """Example test - replace with actual test logic."""
        assert True, "Replace with actual test"
'''

    target_file = tests_dir / f"test_{module_slug}_pw.py"
    target_file.write_text(content)


def _create_api_test(tests_dir: Path, module_slug: str, test_name: str, base_url: str) -> None:
    """Create an API test file."""
    class_name = _class_name(test_name)
    content = f'''"""API tests for {test_name}."""

import pytest
import requests


@pytest.mark.api
class Test{class_name.replace("Page", "")}API:
    """API test suite for {test_name}."""

    BASE_URL = "{base_url}"

    def test_example_api_call(self) -> None:
        """Example API test - replace with actual test logic."""
        response = requests.get(f"{{self.BASE_URL}}/api/endpoint")
        assert response.status_code == 200, "Replace with actual test"
'''

    target_file = tests_dir / f"test_{module_slug}_api.py"
    target_file.write_text(content)


def main(argv: list[str] | None = None) -> int:
    """Entry point for python -m execution."""
    try:
        cli.main(args=argv, standalone_mode=False)
        return 0
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())