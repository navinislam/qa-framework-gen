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
            choices=[
                questionary.Choice("Chrome", value="chrome", checked=True),
                questionary.Choice("Firefox", value="firefox", checked=False),
                questionary.Choice("Edge", value="edge", checked=False),
            ],
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
    # Use package name (underscores) for directory to make it importable
    project_slug = _package_name(name)
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
    # Root __init__.py for IDE/PyCharm code intelligence
    (target_dir / "__init__.py").write_text('"""Test automation framework package."""\n')

    for pages_dir in ["pages", "pages_pw"]:
        if (target_dir / pages_dir).exists():
            (target_dir / pages_dir / "__init__.py").write_text("")

    for tests_dir in ["tests", "tests_pw"]:
        if (target_dir / tests_dir).exists():
            (target_dir / tests_dir / "__init__.py").write_text("")

    # Generate base page classes and example files
    if driver_type in ["selenium", "both"]:
        _create_selenium_base_page(target_dir / "pages")
        _create_example_selenium_page(target_dir / "pages", base_url)
        _create_example_selenium_test(target_dir / "tests")
        _create_selenium_conftest(target_dir, base_url)

    if driver_type in ["playwright", "both"]:
        _create_playwright_base_page(target_dir / "pages_pw", base_url)
        _create_example_playwright_page(target_dir / "pages_pw", base_url)
        _create_example_playwright_test(target_dir / "tests_pw")
        if driver_type == "playwright":
            _create_playwright_conftest(target_dir, base_url)

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


@cli.command()
def add_locators() -> None:
    """Add locator model support for centralized selector management.

    This adds:
    - framework/models/locator.py: Locator dataclass with type safety
    - pages/locators.py: Example locator definitions

    Use this if you want centralized, strongly-typed locators instead of inline tuples.
    """

    # Load config to verify we're in a project
    project_root = Path.cwd()
    config = _load_config(project_root)

    if not config:
        click.echo("❌ Could not find .framework-config.yml. Run this command from a generated project directory.")
        sys.exit(1)

    # Check if this is a Selenium project
    driver_type = config["driver"]["type"]
    if driver_type == "playwright":
        click.echo("⚠️  Locator model is only useful for Selenium projects.")
        click.echo("   Playwright uses simple string selectors (CSS/XPath).")
        if not questionary.confirm("Continue anyway?").ask():
            return

    # Create framework/models directory if it doesn't exist
    models_dir = project_root / "framework" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    # Create __init__.py if it doesn't exist
    models_init = models_dir / "__init__.py"
    if not models_init.exists():
        models_init.write_text('"""Models for the automation framework."""\n')

    # Check if locator.py already exists
    locator_file = models_dir / "locator.py"
    if locator_file.exists():
        if not questionary.confirm(
            "⚠️  framework/models/locator.py already exists. Overwrite?"
        ).ask():
            click.echo("❌ Aborted.")
            return

    # Create the locator model
    _create_locator_model(models_dir)
    click.echo("✅ Created framework/models/locator.py")

    # Create example locators in pages/
    pages_dir = project_root / "pages"
    if pages_dir.exists():
        locators_file = pages_dir / "locators.py"
        if locators_file.exists():
            if questionary.confirm(
                "⚠️  pages/locators.py already exists. Overwrite?"
            ).ask():
                _create_example_locators(pages_dir)
                click.echo("✅ Updated pages/locators.py with examples")
            else:
                click.echo("⏭️  Skipped pages/locators.py (already exists)")
        else:
            _create_example_locators(pages_dir)
            click.echo("✅ Created pages/locators.py with examples")

    # Print usage instructions
    click.echo("")
    click.echo("📝 Locator model added! Here's how to use it:")
    click.echo("")
    click.echo("1. Define locators in pages/locators.py:")
    click.echo("   from framework.models.locator import Locator")
    click.echo("   from selenium.webdriver.common.by import By")
    click.echo("")
    click.echo("   class LoginPageLocators:")
    click.echo("       USERNAME = Locator(By.ID, 'username')")
    click.echo("       PASSWORD = Locator(By.ID, 'password')")
    click.echo("")
    click.echo("2. Use in page objects:")
    click.echo("   from pages.locators import LoginPageLocators")
    click.echo("")
    click.echo("   self.click_element(LoginPageLocators.USERNAME.as_tuple())")
    click.echo("")
    click.echo("See pages/locators.py for more examples!")


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


def _create_locator_model(models_dir: Path) -> None:
    """Create the Locator dataclass model for typed locators."""
    content = '''"""Locator model for strongly-typed Selenium selectors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Union


@dataclass(frozen=True)
class Locator:
    """Strongly typed locator object shared across page objects."""

    by: str
    value: str

    def as_tuple(self) -> Tuple[str, str]:
        """Convert to tuple format for Selenium API."""
        return self.by, self.value


LocatorTuple = Tuple[str, str]
LocatorLike = Union[Locator, LocatorTuple]


def to_locator_tuple(locator: LocatorLike) -> LocatorTuple:
    """Normalize any locator-like input to a tuple the Selenium APIs understand."""
    if isinstance(locator, Locator):
        return locator.as_tuple()
    return locator
'''

    target_file = models_dir / "locator.py"
    target_file.write_text(content)


def _create_example_locators(pages_dir: Path) -> None:
    """Create example locators file to demonstrate the pattern."""
    content = '''"""Example locators demonstrating centralized selector management."""

from selenium.webdriver.common.by import By

from framework.models.locator import Locator


class ExamplePageLocators:
    """Locators for ExamplePage - demonstrates the pattern."""

    # Using Locator dataclass for type safety
    HEADER = Locator(By.TAG_NAME, "h1")
    TITLE = Locator(By.CSS_SELECTOR, "title")

    # You can also use tuples directly
    BODY = (By.TAG_NAME, "body")


class LoginPageLocators:
    """Example locators for a login page."""

    USERNAME = Locator(By.ID, "username")
    PASSWORD = Locator(By.ID, "password")
    LOGIN_BUTTON = Locator(By.ID, "login-button")
    ERROR_MESSAGE = Locator(By.CSS_SELECTOR, ".error-message")
'''

    target_file = pages_dir / "locators.py"
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


def _create_example_selenium_page(pages_dir: Path, base_url: str) -> None:
    """Create example Selenium page object during init."""
    content = f'''"""Example page object for demonstration."""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage


class ExamplePage(BasePage):
    """Example page object demonstrating basic patterns."""

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)
        self.url = "{base_url}"

    def visit(self) -> None:
        """Navigate to the page."""
        self.open(self.url)

    def get_title(self) -> str:
        """Get the page title."""
        return self.driver.title
'''

    target_file = pages_dir / "example_page.py"
    target_file.write_text(content)

    # Update __init__.py
    init_file = pages_dir / "__init__.py"
    init_file.write_text("from .base_page import BasePage\nfrom .example_page import ExamplePage\n")


def _create_example_playwright_page(pages_dir: Path, base_url: str) -> None:
    """Create example Playwright page object during init."""
    content = f'''"""Example page object for demonstration (Playwright)."""

from playwright.async_api import Page

from pages_pw.base_page import BasePage


class ExamplePage(BasePage):
    """Example page object demonstrating basic patterns."""

    def __init__(self, page: Page) -> None:
        super().__init__(page, "{base_url}")

    async def visit(self) -> None:
        """Navigate to the page."""
        await self.navigate_to()

    async def get_title(self) -> str:
        """Get the page title."""
        return await self.page.title()
'''

    target_file = pages_dir / "example_page.py"
    target_file.write_text(content)

    # Update __init__.py
    init_file = pages_dir / "__init__.py"
    init_file.write_text("from .base_page import BasePage\nfrom .example_page import ExamplePage\n")


def _create_example_selenium_test(tests_dir: Path) -> None:
    """Create example Selenium test during init."""
    content = '''"""Example tests demonstrating basic patterns."""

import pytest
from selenium.webdriver.remote.webdriver import WebDriver


@pytest.mark.selenium
@pytest.mark.ui
@pytest.mark.smoke
class TestExample:
    """Example test suite."""

    def test_page_loads(self, driver: WebDriver) -> None:
        """Example test - verify page loads."""
        from pages.example_page import ExamplePage

        page = ExamplePage(driver)
        page.visit()
        assert page.get_title(), "Page title should not be empty"
'''

    target_file = tests_dir / "test_example.py"
    target_file.write_text(content)


def _create_selenium_base_page(pages_dir: Path) -> None:
    """Create Selenium base page class with helper methods."""
    content = '''"""Base page class with reusable Selenium helpers."""

import os
import time
from typing import Callable, Optional, Tuple

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    """Base page class with common Selenium WebDriver operations.

    Includes resilient wait patterns, element state checks, and helper methods
    for common test automation scenarios.
    """

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait_retry_attempts = int(os.getenv("WAITS_RETRY_ATTEMPTS", "3"))
        self.wait_retry_interval = float(os.getenv("WAITS_RETRY_INTERVAL", "0.5"))

    def open(self, url: str) -> None:
        """Navigate to a URL."""
        self.driver.get(url)

    def _wait_with_retry(
        self,
        wait_callable: Callable[[], bool],
        timeout: int,
        retries: Optional[int] = None
    ) -> bool:
        """Execute a wait with retry logic and screenshot on failure.

        Args:
            wait_callable: Function that performs the wait
            timeout: Timeout for each wait attempt
            retries: Number of retry attempts (defaults to WAITS_RETRY_ATTEMPTS env var)

        Returns:
            True if wait succeeded

        Raises:
            Exception: If all retry attempts are exhausted
        """
        attempts = retries if retries is not None else self.wait_retry_attempts
        last_error: Optional[Exception] = None

        for attempt in range(1, attempts + 1):
            try:
                result = wait_callable()
                return result
            except Exception as error:
                last_error = error
                if attempt == attempts:
                    # Take screenshot on final failure
                    self.take_screenshot(f"wait_failure_{int(time.time())}")
                    raise
                time.sleep(self.wait_retry_interval)

        if last_error:
            raise last_error
        return False

    def wait_for_element_present(
        self, locator: Tuple[str, str], timeout: int = 10, retries: Optional[int] = None
    ) -> bool:
        """Wait for an element to be present in the DOM."""
        def wait_callable():
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True

        return self._wait_with_retry(wait_callable, timeout, retries)

    def wait_for_element_visible(
        self, locator: Tuple[str, str], timeout: int = 10, retries: Optional[int] = None
    ) -> bool:
        """Wait for an element to be visible."""
        def wait_callable():
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True

        return self._wait_with_retry(wait_callable, timeout, retries)

    def wait_for_element_clickable(
        self, locator: Tuple[str, str], timeout: int = 10, retries: Optional[int] = None
    ) -> bool:
        """Wait for an element to be clickable."""
        def wait_callable():
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return True

        return self._wait_with_retry(wait_callable, timeout, retries)

    def wait_for_text_to_be_present(
        self, locator: Tuple[str, str], text: str, timeout: int = 10, retries: Optional[int] = None
    ) -> bool:
        """Wait for specific text to appear in an element."""
        def wait_callable():
            WebDriverWait(self.driver, timeout).until(
                EC.text_to_be_present_in_element(locator, text)
            )
            return True

        return self._wait_with_retry(wait_callable, timeout, retries)

    def is_element_present(self, locator: Tuple[str, str]) -> bool:
        """Check if element is present in DOM (does not need to be visible).

        Returns:
            True if element exists, False otherwise (no exception thrown)
        """
        try:
            elements = self.driver.find_elements(*locator)
            return len(elements) > 0
        except Exception:
            return False

    def is_element_displayed(self, locator: Tuple[str, str]) -> bool:
        """Check if element is visible on the page.

        Returns:
            True if element is visible, False otherwise (no exception thrown)
        """
        try:
            return self.driver.find_element(*locator).is_displayed()
        except Exception:
            return False

    def is_element_enabled(self, locator: Tuple[str, str]) -> bool:
        """Check if element is enabled (not disabled).

        Returns:
            True if element is enabled, False otherwise (no exception thrown)
        """
        try:
            return self.driver.find_element(*locator).is_enabled()
        except Exception:
            return False

    def click_element(self, locator: Tuple[str, str], timeout: int = 10) -> None:
        """Wait for element to be clickable and click it."""
        self.wait_for_element_clickable(locator, timeout)
        self.driver.find_element(*locator).click()

    def send_keys_to_element(
        self,
        locator: Tuple[str, str],
        text: str,
        timeout: int = 10,
        submit: bool = False,
        sensitive: bool = False
    ) -> None:
        """Wait for element to be present and send keys to it.

        Args:
            locator: Element locator tuple
            text: Text to send to element
            timeout: Wait timeout in seconds
            submit: If True, submit the form after sending keys
            sensitive: If True, don't log the text (for passwords)
        """
        self.wait_for_element_present(locator, timeout)
        element = self.driver.find_element(*locator)
        element.send_keys(text)

        if submit:
            element.submit()

    def get_text_from_element(
        self, locator: Tuple[str, str], timeout: int = 10
    ) -> str:
        """Wait for element to be present and get its text."""
        self.wait_for_element_present(locator, timeout)
        return self.driver.find_element(*locator).text

    def get_attribute_value(
        self, locator: Tuple[str, str], attribute: str = "value", timeout: int = 10
    ) -> str:
        """Wait for element to be present and get attribute value.

        Args:
            locator: Element locator tuple
            attribute: Attribute name (default: "value" for input fields)
            timeout: Wait timeout in seconds

        Returns:
            Attribute value as string
        """
        self.wait_for_element_present(locator, timeout)
        return self.driver.find_element(*locator).get_attribute(attribute) or ""

    def clear_element_text(self, locator: Tuple[str, str], timeout: int = 10) -> None:
        """Clear text from an input field using backspace.

        Some input fields don't respond to .clear(), so this uses backspace.
        """
        self.wait_for_element_present(locator, timeout)
        element = self.driver.find_element(*locator)
        element.click()

        # Get current value and clear it with backspace
        current_value = element.get_attribute("value") or ""
        for _ in range(len(current_value) + 1):  # +1 to ensure all cleared
            element.send_keys(Keys.BACK_SPACE)

    def take_screenshot(self, filename: str) -> str:
        """Take a screenshot and save to file with timestamp.

        Args:
            filename: Base filename (timestamp will be appended)

        Returns:
            Full screenshot filename
        """
        timestamp = time.strftime("%m%d%Y%H%M%S")
        screenshot_name = f"{filename}_{timestamp}.png"
        self.driver.save_screenshot(screenshot_name)
        return screenshot_name
'''

    target_file = pages_dir / "base_page.py"
    target_file.write_text(content)


def _create_playwright_base_page(pages_dir: Path, base_url: str) -> None:
    """Create Playwright base page class with helper methods."""
    content = f'''"""Base page class with reusable Playwright helpers."""

from typing import List, Optional

from playwright.async_api import Page


class BasePage:
    """Base page class with common Playwright operations.

    Includes navigation, element interaction, state checks, form handling,
    and advanced helpers for comprehensive test automation.
    """

    def __init__(self, page: Page, base_url: str | None = None) -> None:
        self.page = page
        self.base_url = (base_url or "{base_url}").rstrip("/")

    # Navigation Methods

    async def navigate_to(self, path: str = "") -> None:
        """Navigate to a path relative to base_url."""
        url = f"{{self.base_url}}/{{path.lstrip('/')}}" if path else self.base_url
        await self.page.goto(url)

    async def reload(self) -> None:
        """Reload the current page."""
        await self.page.reload()

    async def go_back(self) -> None:
        """Navigate back in browser history."""
        await self.page.go_back()

    async def go_forward(self) -> None:
        """Navigate forward in browser history."""
        await self.page.go_forward()

    async def wait_for_url(self, url_pattern: str, timeout: int = 30000) -> None:
        """Wait for URL to match pattern (supports regex).

        Args:
            url_pattern: URL string or regex pattern
            timeout: Wait timeout in milliseconds
        """
        await self.page.wait_for_url(url_pattern, timeout=timeout)

    # Element Interaction Methods

    async def click(self, selector: str, timeout: Optional[int] = None) -> None:
        """Click an element.

        Args:
            selector: CSS or XPath selector
            timeout: Optional timeout in milliseconds
        """
        await self.page.locator(selector).click(timeout=timeout)

    async def double_click(self, selector: str, timeout: Optional[int] = None) -> None:
        """Double click an element."""
        await self.page.locator(selector).dblclick(timeout=timeout)

    async def hover(self, selector: str, timeout: Optional[int] = None) -> None:
        """Hover over an element."""
        await self.page.locator(selector).hover(timeout=timeout)

    async def fill(self, selector: str, text: str, timeout: Optional[int] = None) -> None:
        """Fill an input field (clears first, then types).

        Args:
            selector: CSS or XPath selector
            text: Text to fill
            timeout: Optional timeout in milliseconds
        """
        await self.page.locator(selector).fill(text, timeout=timeout)

    async def type(self, selector: str, text: str, delay: int = 0) -> None:
        """Type text into an element (simulates keyboard, no clear).

        Args:
            selector: CSS or XPath selector
            text: Text to type
            delay: Delay between keystrokes in milliseconds
        """
        await self.page.locator(selector).type(text, delay=delay)

    async def clear(self, selector: str) -> None:
        """Clear an input field."""
        await self.page.locator(selector).clear()

    async def press_key(self, selector: str, key: str) -> None:
        """Press a key on an element.

        Args:
            selector: CSS or XPath selector
            key: Key name (e.g., "Enter", "Escape", "ArrowDown")
        """
        await self.page.locator(selector).press(key)

    # Form Handling Methods

    async def check(self, selector: str) -> None:
        """Check a checkbox (ensures it's checked)."""
        await self.page.locator(selector).check()

    async def uncheck(self, selector: str) -> None:
        """Uncheck a checkbox (ensures it's unchecked)."""
        await self.page.locator(selector).uncheck()

    async def select_option(
        self,
        selector: str,
        value: Optional[str] = None,
        label: Optional[str] = None,
        index: Optional[int] = None
    ) -> None:
        """Select option from dropdown.

        Args:
            selector: CSS or XPath selector for <select> element
            value: Select by value attribute
            label: Select by visible text
            index: Select by index (0-based)
        """
        if value:
            await self.page.locator(selector).select_option(value=value)
        elif label:
            await self.page.locator(selector).select_option(label=label)
        elif index is not None:
            await self.page.locator(selector).select_option(index=index)
        else:
            raise ValueError("Must provide value, label, or index")

    # Text and Attribute Methods

    async def get_text(self, selector: str) -> str:
        """Get text content from an element.

        Returns:
            Text content (empty string if no text)
        """
        return await self.page.locator(selector).text_content() or ""

    async def get_inner_text(self, selector: str) -> str:
        """Get inner text from an element (rendered text).

        Returns:
            Inner text (empty string if no text)
        """
        return await self.page.locator(selector).inner_text()

    async def get_input_value(self, selector: str) -> str:
        """Get value from input field.

        Returns:
            Input value (empty string if no value)
        """
        return await self.page.locator(selector).input_value()

    async def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get any attribute from an element.

        Args:
            selector: CSS or XPath selector
            attribute: Attribute name (e.g., "href", "class", "disabled")

        Returns:
            Attribute value or None if not present
        """
        return await self.page.locator(selector).get_attribute(attribute)

    async def get_all_text_contents(self, selector: str) -> List[str]:
        """Get text from all matching elements.

        Returns:
            List of text contents from all matching elements
        """
        return await self.page.locator(selector).all_text_contents()

    # Element State Check Methods

    async def is_present(self, selector: str) -> bool:
        """Check if element exists in DOM (doesn't need to be visible).

        Returns:
            True if element exists, False otherwise
        """
        return await self.page.locator(selector).count() > 0

    async def is_visible(self, selector: str) -> bool:
        """Check if element is visible.

        Returns:
            True if visible, False otherwise
        """
        try:
            return await self.page.locator(selector).is_visible()
        except Exception:
            return False

    async def is_enabled(self, selector: str) -> bool:
        """Check if element is enabled (not disabled).

        Returns:
            True if enabled, False otherwise
        """
        try:
            return await self.page.locator(selector).is_enabled()
        except Exception:
            return False

    async def is_checked(self, selector: str) -> bool:
        """Check if checkbox/radio is checked.

        Returns:
            True if checked, False otherwise
        """
        try:
            return await self.page.locator(selector).is_checked()
        except Exception:
            return False

    async def is_editable(self, selector: str) -> bool:
        """Check if element is editable.

        Returns:
            True if editable, False otherwise
        """
        try:
            return await self.page.locator(selector).is_editable()
        except Exception:
            return False

    # Wait Methods

    async def wait_for_selector(
        self,
        selector: str,
        state: str = "visible",
        timeout: Optional[int] = None
    ) -> None:
        """Wait for a selector to be in the desired state.

        Args:
            selector: CSS or XPath selector
            state: State to wait for ("attached", "detached", "visible", "hidden")
            timeout: Timeout in milliseconds
        """
        await self.page.locator(selector).wait_for(state=state, timeout=timeout)

    async def wait_for_text(
        self,
        selector: str,
        text: str,
        timeout: int = 30000
    ) -> None:
        """Wait for specific text to appear in an element.

        Args:
            selector: CSS or XPath selector
            text: Text to wait for
            timeout: Timeout in milliseconds
        """
        await self.page.locator(selector).wait_for(state="visible", timeout=timeout)
        locator = self.page.locator(selector)
        # Wait until the locator contains the expected text
        await self.page.wait_for_function(
            f"element => element.textContent.includes('{{text}}')",
            locator,
            timeout=timeout
        )

    # Screenshot and Debug Methods

    async def take_screenshot(self, path: str, full_page: bool = True) -> bytes:
        """Take a screenshot and save to file.

        Args:
            path: File path to save screenshot
            full_page: If True, capture full scrollable page

        Returns:
            Screenshot bytes
        """
        return await self.page.screenshot(path=path, full_page=full_page)

    async def take_element_screenshot(self, selector: str, path: str) -> bytes:
        """Take a screenshot of a specific element.

        Args:
            selector: CSS or XPath selector
            path: File path to save screenshot

        Returns:
            Screenshot bytes
        """
        return await self.page.locator(selector).screenshot(path=path)
'''

    target_file = pages_dir / "base_page.py"
    target_file.write_text(content)


def _create_selenium_conftest(project_dir: Path, base_url: str) -> None:
    """Create conftest.py with Selenium driver fixtures."""
    content = f'''"""Pytest configuration and fixtures for Selenium tests."""

import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService


@pytest.fixture(scope="function")
def driver():
    """Create and tear down a WebDriver instance."""
    browser = os.getenv("BROWSER", "chrome").lower()
    headless = os.getenv("HEADLESS", "false").lower() == "true"

    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=options)
    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
    else:
        raise ValueError(f"Unsupported browser: {{browser}}")

    driver.maximize_window()
    yield driver
    driver.quit()


@pytest.fixture(scope="session")
def base_url():
    """Return the base URL for the application under test."""
    return os.getenv("BASE_URL", "{base_url}")
'''

    target_file = project_dir / "conftest.py"
    target_file.write_text(content)


def _create_playwright_conftest(project_dir: Path, base_url: str) -> None:
    """Create conftest.py with Playwright fixtures."""
    content = f'''"""Pytest configuration and fixtures for Playwright tests."""

import os

import pytest


@pytest.fixture(scope="session")
def base_url():
    """Return the base URL for the application under test."""
    return os.getenv("BASE_URL", "{base_url}")
'''

    target_file = project_dir / "conftest.py"
    target_file.write_text(content)


def _create_example_playwright_test(tests_dir: Path) -> None:
    """Create example Playwright test during init."""
    content = '''"""Example tests demonstrating basic patterns (Playwright)."""

import pytest
from playwright.async_api import Page


@pytest.mark.playwright
@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.asyncio
class TestExamplePlaywright:
    """Example Playwright test suite."""

    async def test_page_loads(self, page: Page) -> None:
        """Example test - verify page loads."""
        from pages_pw.example_page import ExamplePage

        example_page = ExamplePage(page)
        await example_page.visit()
        title = await example_page.get_title()
        assert title, "Page title should not be empty"
'''

    target_file = tests_dir / "test_example_pw.py"
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