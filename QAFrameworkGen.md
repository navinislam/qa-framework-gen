# QA Framework Generator (qa-framework-gen) - Technical Specification

**Version:** 1.0.0
**Created:** 2025-10-29
**Status:** Draft - Awaiting Approval

---

## 1. Executive Summary

### 1.1 Purpose
Create a CLI tool (`qa-framework-gen`) that scaffolds production-ready pytest automation projects with optional Selenium WebDriver and/or Playwright support, following Page Object Model patterns with built-in quality tooling, Docker support, and CI/CD integration.

### 1.2 Target Audience
- **Primary**: SDETs and Developers who need to quickly bootstrap test automation projects
- **Skill Level**: Intermediate to advanced (familiarity with pytest, OOP, and test automation patterns)

### 1.3 Success Criteria
- ✅ Users can generate a working automation project in < 2 minutes
- ✅ Generated projects include working example tests
- ✅ Framework supports both Selenium and Playwright with consistent patterns
- ✅ Projects can be extended without modifying framework core
- ✅ Documentation enables users to customize and enhance generated code

---

## 2. Product Scope

### 2.1 In Scope
- **New project scaffolding** with interactive CLI prompts
- **Multi-project workspace** support (manage multiple test projects)
- **Driver options**: Selenium only, Playwright only, or both
- **Optional features**: Docker, CI/CD, Allure, quality tools, API testing
- **Page object generators** for adding new pages post-initialization
- **Test generators** for creating test file boilerplate
- **Minimal example tests** (login flow for UI, simple GET request for API)
- **Tutorial-style README documentation**
- **GitHub-only distribution** (no PyPI initially)

### 2.2 Out of Scope (Future Considerations)
- ❌ Migrating existing projects to framework
- ❌ Visual regression testing (Percy/Applitools)
- ❌ Advanced test data encryption (Vault integration)
- ❌ Windows support (Unix/macOS only)
- ❌ Tool installation validation during `init`
- ❌ Automatic framework upgrades with merge conflict resolution

### 2.3 Non-Goals
- Building a test execution platform (use pytest-xdist)
- Creating a test case management system
- Providing cloud service integrations (BrowserStack, Sauce Labs)

### 2.4 Installation & Distribution Strategy

#### 2.4.1 Distribution Method
**Primary**: GitHub repository with pip/pipx installation
- Repository: `https://github.com/navinislam/qa-framework-gen`
- No PyPI publishing initially (keep development agile)
- Future: Publish to PyPI when stable (v1.0+ release)

#### 2.4.2 Installation Methods

**Recommended: pipx (isolated installation)**
```bash
# Install pipx if not already installed
pip install pipx
pipx ensurepath

# Install qa-framework-gen from GitHub
pipx install git+https://github.com/navinislam/qa-framework-gen.git

# Verify installation
qfg --version
qfg --help
```

**Benefits**:
- ✅ Isolated environment (no dependency conflicts)
- ✅ `qfg` command available globally
- ✅ Easy upgrades: `pipx upgrade qa-framework-gen`
- ✅ Industry best practice for CLI tools

**Alternative 1: Direct pip installation**
```bash
pip install git+https://github.com/navinislam/qa-framework-gen.git
```

**Alternative 2: Editable installation (for contributors)**
```bash
git clone https://github.com/navinislam/qa-framework-gen.git
cd qa-framework-gen
pip install -e .  # Or: poetry install
```

#### 2.4.3 Entry Point Configuration

**pyproject.toml**:
```toml
[project.scripts]
qfg = "framework.cli.__main__:cli"
```

This creates the `qfg` executable when installed, pointing to the Click CLI entry point.

#### 2.4.4 Two-Phase Installation Model

**Phase 1: Install Generator Tool (ONE TIME)**
```bash
pipx install git+https://github.com/navinislam/qa-framework-gen.git
```
- Framework generator installed globally
- `qfg` command available system-wide
- No need to reinstall for each project

**Phase 2: Set Up Generated Project (PER PROJECT)**
```bash
qfg init my-tests
cd my-tests
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
- Each project has its own virtual environment
- Each project has its own dependencies (pytest, selenium, playwright, etc.)
- Generator tool remains separate from project dependencies

#### 2.4.5 Upgrade Strategy

**Framework Tool Upgrades**:
```bash
# With pipx
pipx upgrade qa-framework-gen

# With pip
pip install --upgrade git+https://github.com/navinislam/qa-framework-gen.git
```

**Generated Project Upgrades** (future feature):
```bash
cd my-tests
qfg upgrade  # Updates templates, configs to match new framework version
```

#### 2.4.6 Version Requirements
- **Python**: 3.11+ (for framework tool and generated projects)
- **pip**: 23.0+ (for modern dependency resolution)
- **pipx**: 1.4.0+ (recommended)
- **Git**: 2.30+ (for GitHub installation)

---

## 3. Technical Architecture

### 3.1 Project Structure

```
qa-framework-gen/                    # Framework repository
├── framework/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── __main__.py              # Entry point: python -m framework.cli
│   │   ├── commands/
│   │   │   ├── __init__.py
│   │   │   ├── init.py              # qfg init command
│   │   │   ├── add_page.py          # qfg add-page command
│   │   │   ├── add_test.py          # qfg add-test command
│   │   │   ├── config.py            # qfg config command
│   │   │   └── validate.py          # qfg validate command
│   │   ├── prompts.py               # Interactive prompts using questionary
│   │   └── validators.py            # Input validation logic
│   ├── templates/                   # Jinja2 templates
│   │   ├── base_project/
│   │   │   ├── .gitignore.j2
│   │   │   ├── pytest.ini.j2
│   │   │   ├── pyproject.toml.j2
│   │   │   ├── requirements.txt.j2
│   │   │   ├── .envrc.j2
│   │   │   ├── Makefile.j2
│   │   │   └── README.md.j2
│   │   ├── selenium/
│   │   │   ├── pages/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_page.py.j2
│   │   │   │   ├── locators.py.j2
│   │   │   │   └── login_page.py.j2  # Example page object
│   │   │   ├── tests/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── conftest.py.j2
│   │   │   │   └── test_login.py.j2  # Example test
│   │   │   └── data/
│   │   │       └── login_users.yml
│   │   ├── playwright/
│   │   │   ├── pages/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_page_pw.py.j2
│   │   │   │   └── login_page_pw.py.j2  # Example async page object
│   │   │   └── tests/
│   │   │       ├── __init__.py
│   │   │       ├── conftest_pw.py.j2
│   │   │       └── test_login_pw.py.j2  # Example async test
│   │   ├── api/
│   │   │   ├── clients/
│   │   │   │   ├── __init__.py
│   │   │   │   └── base_client.py.j2  # requests wrapper
│   │   │   └── tests/
│   │   │       ├── __init__.py
│   │   │       └── test_api_example.py.j2
│   │   ├── docker/
│   │   │   ├── Dockerfile.j2
│   │   │   ├── docker-compose.local.yml.j2
│   │   │   ├── docker-compose.yml.j2
│   │   │   └── wait-for-grid.sh
│   │   ├── ci/
│   │   │   └── github_workflows_test.yml.j2
│   │   └── quality/
│   │       ├── .pre-commit-config.yaml.j2
│   │       ├── pyproject_quality.toml.j2  # black, isort config
│   │       └── .flake8.j2
│   └── generators/
│       ├── __init__.py
│       ├── project.py               # ProjectGenerator class
│       ├── page_object.py           # PageObjectGenerator class
│       ├── test.py                  # TestGenerator class
│       └── workspace.py             # WorkspaceManager class
├── tests/                           # Framework self-tests
│   ├── unit/
│   │   ├── test_generators.py
│   │   └── test_validators.py
│   └── integration/
│       └── test_project_generation.py
├── README.md                        # Comprehensive tutorial-style docs
├── pyproject.toml                   # Poetry/setuptools config
├── setup.py                         # Installation script
└── .framework-root                  # Marker file for workspace root
```

### 3.2 Generated Project Structure

**Example: User runs `qfg init my-tests --driver both --api`**

```
my-tests/                            # Generated project
├── .framework-config.yml            # Framework metadata for upgrades
├── .gitignore
├── pytest.ini
├── pyproject.toml
├── requirements.txt
├── .envrc                           # Environment variables (direnv)
├── Makefile                         # Common commands
├── README.md                        # Project-specific documentation
├── pages/                           # Selenium page objects
│   ├── __init__.py
│   ├── base_page.py
│   ├── locators.py
│   └── login_page.py                # Example
├── pages_pw/                        # Playwright page objects (if both selected)
│   ├── __init__.py
│   ├── base_page_pw.py
│   └── login_page_pw.py             # Example
├── api/                             # API testing (if enabled)
│   ├── __init__.py
│   ├── clients/
│   │   ├── __init__.py
│   │   └── base_client.py
│   └── tests/
│       ├── __init__.py
│       └── test_api_example.py
├── tests/                           # Selenium tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── data/
│   │   └── login_users.yml
│   └── test_login.py                # Example
├── tests_pw/                        # Playwright tests (if both selected)
│   ├── __init__.py
│   ├── conftest.py
│   └── test_login_pw.py             # Example
├── docker/                          # Docker files (if enabled)
│   ├── Dockerfile
│   ├── docker-compose.local.yml
│   ├── docker-compose.yml
│   └── wait-for-grid.sh
└── .github/                         # CI/CD (if enabled)
    └── workflows/
        └── test.yml
```

### 3.3 Technology Stack

| Component | Technology | Justification |
|-----------|------------|---------------|
| CLI Framework | **Click** | Industry standard, excellent for complex CLI apps |
| Interactive Prompts | **questionary** | Better UX than raw input(), supports validation |
| Templating | **Jinja2** | Powerful conditionals, filters, template inheritance |
| Configuration | **YAML** (PyYAML) | Human-readable, supports comments |
| Logging | **structlog** | Consistent with current BaseFactory |
| Python Version | **3.11+** | Modern type hints, better performance |
| Package Manager | **Poetry** | Dependency resolution, easy publishing |

---

## 4. Feature Specifications

### 4.1 CLI Commands

#### 4.1.1 `qfg init [PROJECT_NAME]`

**Purpose**: Create a new automation project with interactive configuration.

**Syntax**:
```bash
qfg init [PROJECT_NAME] [OPTIONS]
```

**Options**:
- `--driver [selenium|playwright|both]`: Skip driver selection prompt
- `--base-url URL`: Skip base URL prompt
- `--no-interactive`: Use all defaults (minimal project)
- `--template [minimal|standard|full]`: Preset bundle (future feature)

**Interactive Prompts** (if `--no-interactive` not specified):

1. **Project Name** (if not provided as argument)
   - Validation: alphanumeric + hyphens/underscores, no spaces
   - Default: current directory name

2. **Base URL**
   - Validation: valid URL with scheme (http/https)
   - Example: `https://www.saucedemo.com`
   - Default: `https://example.com`

3. **Driver Selection** (multi-choice)
   - Options: `Selenium`, `Playwright`, `Both`
   - Default: `Selenium`

4. **Browser Support** (multi-select, only if Selenium selected)
   - Options: `Chrome`, `Firefox`, `Edge`
   - Default: `Chrome`
   - Note: Playwright supports all browsers by default

5. **Optional Features** (yes/no for each):
   - Docker support (Selenium Grid + test container)
   - GitHub Actions CI/CD
   - Allure reporting
   - Code quality tools (black, flake8, mypy, bandit)
   - Pre-commit hooks
   - Parallel execution (pytest-xdist)
   - Flaky test retry (pytest-rerunfailures)
   - API testing support

6. **Logging Mode** (single choice)
   - Options: `JSON` (structlog), `Console` (plain text), `Both`
   - Default: `JSON`

7. **Test Data Format** (single choice)
   - Options: `YAML`, `JSON`
   - Default: `YAML`

**Output**:
```
✨ Generating project: my-tests
📁 Creating directory structure...
📝 Rendering templates...
📦 Generating requirements.txt...
✅ Project created successfully!

Next steps:
  cd my-tests
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  pytest tests/ -v
```

**Generated Files**:
- `.framework-config.yml`: Stores user selections for future reference
- All project files based on selections

**`.framework-config.yml` Example**:
```yaml
framework:
  version: "1.0.0"
  generator: "qa-framework-gen"
  created: "2025-10-29T10:30:00Z"

project:
  name: "my-tests"
  base_url: "https://www.saucedemo.com"

driver:
  type: "both"  # selenium, playwright, both
  browsers:
    - chrome
    - firefox

features:
  docker: true
  ci_cd: true
  allure: true
  quality_tools: true
  pre_commit: true
  parallel: true
  flaky_retry: true
  api_testing: false

settings:
  logging_mode: "json"
  test_data_format: "yaml"
  playwright_async: true
```

---

#### 4.1.2 `qfg add-page PAGE_NAME`

**Purpose**: Generate a new page object with locators and basic structure.

**Syntax**:
```bash
qfg add-page PAGE_NAME [OPTIONS]
```

**Options**:
- `--driver [selenium|playwright|both]`: Override driver from `.framework-config.yml`
- `--url PATH`: Page URL path (e.g., `/inventory`)

**Behavior**:
- **Reads `.framework-config.yml`** to determine:
  - Driver type (selenium, playwright, or both)
  - Base URL for constructing page URLs
- Command must be run from within a generated project directory
- Automatically detects project configuration

**Interactive Prompts**:

1. **Driver** (ONLY if `--driver` not specified AND config shows both drivers)
   - Options: `Selenium`, `Playwright`, `Both`
   - If config has only one driver, automatically uses that driver
   - Example: If `.framework-config.yml` shows `driver.type: selenium`, generates Selenium page object without prompting

2. **Page URL Path** (if `--url` not specified)
   - Example: `/inventory` → becomes `https://base-url-from-config/inventory`
   - Base URL automatically read from `.framework-config.yml` (`project.base_url`)

3. **Add example locator?** (yes/no)
   - If yes, prompts for locator name and selector

**Output**:
```
✨ Generating page object: InventoryPage
📝 Created: pages/inventory_page.py
📝 Updated: pages/locators.py (added InventoryPageLocators)
✅ Page object created successfully!

Next steps:
  1. Add locators to pages/locators.py (InventoryPageLocators enum)
  2. Implement page methods in pages/inventory_page.py
  3. Add fixture to tests/conftest.py if needed
```

**Generated Code** (Selenium example):

`pages/inventory_page.py`:
```python
"""Inventory page object for Selenium WebDriver."""
from pages.base_page import BaseFactory
from pages.locators import InventoryPageLocators


class InventoryPage(BaseFactory):
    """Page object for /inventory page."""

    def __init__(self, base_factory: BaseFactory):
        """Initialize with existing driver."""
        super().__init__(base_factory.driver)
        self.url = f"{self.base_url}/inventory"

    def navigate(self):
        """Navigate to inventory page."""
        self.driver.get(self.url)
        return self

    # TODO: Add page-specific methods here
```

`pages/locators.py` (appends new enum):
```python
class InventoryPageLocators(Enum):
    """Locators for Inventory page."""
    # TODO: Add locators here
    # EXAMPLE_BUTTON = Locator(By.ID, "example-button")
```

---

#### 4.1.3 `qfg add-test TEST_NAME`

**Purpose**: Generate a new test file with boilerplate structure.

**Syntax**:
```bash
qfg add-test TEST_NAME [OPTIONS]
```

**Options**:
- `--driver [selenium|playwright|both]`: Override driver from `.framework-config.yml`
- `--type [ui|api]`: Test type (defaults to ui)

**Behavior**:
- **Reads `.framework-config.yml`** to determine:
  - Driver type (selenium, playwright, or both)
  - API testing enabled status
- Command must be run from within a generated project directory
- Automatically detects project configuration

**Interactive Prompts**:

1. **Driver** (ONLY if `--driver` not specified AND config shows both drivers)
   - Options: `Selenium`, `Playwright`, `Both`
   - If config has only one driver, automatically uses that driver
   - Example: If `.framework-config.yml` shows `driver.type: playwright`, generates Playwright test without prompting

2. **Test Type** (if `--type` not specified)
   - Options: `UI`, `API` (API only shown if enabled in config)
   - Automatically reads from `.framework-config.yml` (`features.api_testing`)
   - If API testing not enabled, defaults to UI without prompting

3. **Add example test case?** (yes/no)

**Output**:
```
✨ Generating test file: test_checkout.py
📝 Created: tests/test_checkout.py
✅ Test file created successfully!

Run with: pytest tests/test_checkout.py -v
```

**Generated Code** (Selenium example):

`tests/test_checkout.py`:
```python
"""Checkout flow tests."""
import allure
import pytest


@allure.epic("E-commerce")
@allure.feature("Checkout")
class TestCheckout:
    """Checkout flow test cases."""

    @allure.story("User completes purchase")
    @pytest.mark.ui
    @pytest.mark.smoke
    def test_example(self, login, inventory):
        """Example test case - replace with actual test."""
        # TODO: Implement test logic
        assert True  # Replace with actual assertion
```

---

#### 4.1.4 `qfg config`

**Purpose**: Display current project configuration.

**Syntax**:
```bash
qfg config [OPTIONS]
```

**Options**:
- `--show-paths`: Include file paths in output
- `--json`: Output as JSON instead of pretty print

**Output**:
```
📋 Project Configuration

Project: my-tests
Base URL: https://www.saucedemo.com
Framework Version: 1.0.0

Drivers:
  - Selenium (Chrome, Firefox)
  - Playwright (async)

Features:
  ✅ Docker support
  ✅ GitHub Actions CI/CD
  ✅ Allure reporting
  ✅ Code quality tools
  ✅ Pre-commit hooks
  ✅ Parallel execution
  ❌ API testing

Settings:
  Logging: JSON
  Test Data: YAML
```

---

#### 4.1.5 `qfg validate`

**Purpose**: Validate project structure against framework expectations.

**Syntax**:
```bash
qfg validate
```

**Validation Checks**:
- ✅ `.framework-config.yml` exists and is valid YAML
- ✅ Required directories exist (pages/, tests/)
- ✅ Required files exist (pytest.ini, conftest.py)
- ✅ Page objects inherit from BaseFactory/BasePage
- ✅ Test files follow naming convention (`test_*.py`)
- ⚠️ Warnings for missing optional files (Makefile, .pre-commit-config.yaml)

**Output**:
```
🔍 Validating project structure...

✅ Configuration file valid
✅ Directory structure correct
✅ Page objects properly structured
⚠️  Warning: Makefile not found (optional)
✅ All required tests/ files present

Validation complete: 4 passed, 0 failed, 1 warning
```

---

### 4.2 Workspace Management

**Concept**: Users can manage multiple test projects from a single framework installation.

**Workspace Structure**:
```
~/automation/                        # Workspace root
├── .framework-root                  # Marker file (empty)
├── project-a/
│   ├── .framework-config.yml
│   └── ...
├── project-b/
│   ├── .framework-config.yml
│   └── ...
└── shared/                          # Optional shared utilities
    └── helpers.py
```

**Workspace Detection**:
- CLI commands search upward for `.framework-root` marker
- If found, commands know they're in a multi-project workspace
- If not found, treat current directory as single project

**Future Command** (not MVP):
```bash
qfg workspace init         # Create workspace root
qfg workspace list         # Show all projects
qfg workspace upgrade-all  # Upgrade all projects
```

---

### 4.3 Template System

#### 4.3.1 Jinja2 Template Variables

**Global Variables** (available in all templates):
```jinja2
{{ project_name }}           # my-tests
{{ base_url }}               # https://www.saucedemo.com
{{ framework_version }}      # 1.0.0
{{ created_date }}           # 2025-10-29
{{ python_version }}         # 3.11
```

**Feature Flags** (boolean conditionals):
```jinja2
{% if use_selenium %}...{% endif %}
{% if use_playwright %}...{% endif %}
{% if use_both_drivers %}...{% endif %}
{% if use_docker %}...{% endif %}
{% if use_ci_cd %}...{% endif %}
{% if use_allure %}...{% endif %}
{% if use_quality_tools %}...{% endif %}
{% if use_api_testing %}...{% endif %}
```

**Lists**:
```jinja2
{{ browsers }}               # ['chrome', 'firefox']
{% for browser in browsers %}
  - {{ browser }}
{% endfor %}
```

#### 4.3.2 Template Inheritance Example

`base_project/README.md.j2`:
```jinja2
# {{ project_name }}

Automated testing project generated by qa-framework-gen.

## Quick Start

{% if use_selenium %}
### Selenium Tests
```bash
pytest tests/ -v
```
{% endif %}

{% if use_playwright %}
### Playwright Tests
```bash
pytest tests_pw/ -v
```
{% endif %}

{% if use_docker %}
## Docker Execution
```bash
make test-local  # Selenium Grid
```
{% endif %}

## Configuration

Base URL: {{ base_url }}
{% if use_selenium %}
Browsers: {{ browsers|join(', ') }}
{% endif %}
```

#### 4.3.3 Custom Template Overrides

**User can create** (in their generated project):
```
my-tests/.framework/templates/
└── pages/
    └── custom_base_page.py.j2
```

**Future feature**: `qfg add-page` will use custom template if it exists.

---

### 4.4 Example Tests & Page Objects

#### 4.4.1 Selenium Example (Login Flow)

**pages/locators.py**:
```python
"""Centralized locator definitions."""
from dataclasses import dataclass
from enum import Enum
from selenium.webdriver.common.by import By


@dataclass(frozen=True)
class Locator:
    """Typed locator with strategy and value."""
    by: str
    value: str


class LoginPageLocators(Enum):
    """Login page element locators."""
    USERNAME = Locator(By.ID, "user-name")
    PASSWORD = Locator(By.ID, "password")
    LOGIN_BUTTON = Locator(By.ID, "login-button")
    ERROR_MESSAGE = Locator(By.CSS_SELECTOR, "[data-test='error']")
```

**pages/login_page.py**:
```python
"""Login page object."""
from pages.base_page import BaseFactory
from pages.locators import LoginPageLocators


class LoginPage(BaseFactory):
    """Page object for login functionality."""

    def __init__(self, base_factory: BaseFactory):
        """Initialize with existing driver."""
        super().__init__(base_factory.driver)
        self.url = f"{self.base_url}/login"

    def navigate(self):
        """Navigate to login page."""
        self.driver.get(self.url)
        return self

    def login_as(self, username: str, password: str):
        """Perform login action."""
        self.send_keys_to_element(
            LoginPageLocators.USERNAME.value,
            username
        )
        self.send_keys_to_element(
            LoginPageLocators.PASSWORD.value,
            password,
            sensitive=True
        )
        self.click_element(LoginPageLocators.LOGIN_BUTTON.value)
        return self

    def get_error_message(self) -> str:
        """Return error message text."""
        element = self.wait_for_element_present(
            LoginPageLocators.ERROR_MESSAGE.value
        )
        return element.text
```

**tests/test_login.py**:
```python
"""Login functionality tests."""
import allure
import pytest


@allure.epic("Authentication")
@allure.feature("Login")
class TestLogin:
    """Login page test cases."""

    @allure.story("Valid login")
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_successful_login(self, login):
        """User can login with valid credentials."""
        login.navigate()
        login.login_as("standard_user", "secret_sauce")

        # Verify redirect to inventory page
        assert "/inventory.html" in login.driver.current_url

    @allure.story("Invalid login")
    @pytest.mark.ui
    def test_invalid_credentials(self, login):
        """User sees error with invalid credentials."""
        login.navigate()
        login.login_as("invalid_user", "wrong_password")

        error = login.get_error_message()
        assert "do not match" in error.lower()
```

#### 4.4.2 Playwright Example (Async Login Flow)

**pages_pw/login_page_pw.py**:
```python
"""Login page object for Playwright."""
from playwright.async_api import Page


class LoginPagePW:
    """Async page object for login functionality."""

    def __init__(self, page: Page, base_url: str):
        """Initialize with Playwright page."""
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/login"

    async def navigate(self):
        """Navigate to login page."""
        await self.page.goto(self.url)
        return self

    async def login_as(self, username: str, password: str):
        """Perform login action."""
        await self.page.fill("#user-name", username)
        await self.page.fill("#password", password)
        await self.page.click("#login-button")
        return self

    async def get_error_message(self) -> str:
        """Return error message text."""
        return await self.page.text_content("[data-test='error']")
```

**tests_pw/test_login_pw.py**:
```python
"""Login functionality tests (Playwright)."""
import allure
import pytest
from playwright.async_api import Page


@allure.epic("Authentication")
@allure.feature("Login")
@pytest.mark.playwright
class TestLoginPW:
    """Playwright login test cases."""

    @allure.story("Valid login")
    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_successful_login(self, page: Page, login_page_pw):
        """User can login with valid credentials."""
        await login_page_pw.navigate()
        await login_page_pw.login_as("standard_user", "secret_sauce")

        await page.wait_for_url("**/inventory.html")
        assert "/inventory.html" in page.url
```

#### 4.4.3 API Testing Example (if enabled)

**api/clients/base_client.py**:
```python
"""Base API client with common functionality."""
import os
import requests
from typing import Dict, Any


class BaseAPIClient:
    """Base class for API clients."""

    def __init__(self):
        """Initialize with base URL from environment."""
        self.base_url = os.getenv("API_BASE_URL", "https://api.example.com")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """Perform GET request."""
        url = f"{self.base_url}{endpoint}"
        return self.session.get(url, **kwargs)

    def post(self, endpoint: str, data: Dict[str, Any], **kwargs) -> requests.Response:
        """Perform POST request."""
        url = f"{self.base_url}{endpoint}"
        return self.session.post(url, json=data, **kwargs)
```

**api/tests/test_api_example.py**:
```python
"""Example API tests."""
import allure
import pytest


@allure.epic("API")
@allure.feature("Users")
@pytest.mark.api
class TestUsersAPI:
    """User API endpoint tests."""

    @allure.story("Get user list")
    def test_get_users(self, api_client):
        """GET /users returns user list."""
        response = api_client.get("/users")

        assert response.status_code == 200
        assert isinstance(response.json(), list)
```

---

### 4.5 Configuration & Environment Management

#### 4.5.1 Environment Variables

**Generated `.envrc`** (for use with direnv):
```bash
# Base configuration
export URI={{ base_url }}
export BROWSER=chrome
export LOG_MODE=json

# Selenium Grid (optional)
# export HUB=http://localhost:4444/wd/hub

# API testing (if enabled)
{% if use_api_testing %}
export API_BASE_URL=https://api.example.com
{% endif %}

# Wait configuration
export WAITS_RETRY_ATTEMPTS=3
export WAITS_RETRY_INTERVAL=0.5

# Playwright (if enabled)
{% if use_playwright %}
export HEADLESS=true
{% endif %}
```

#### 4.5.2 pytest.ini

```ini
[pytest]
minversion = 7.0
testpaths = tests{% if use_playwright %} tests_pw{% endif %}{% if use_api_testing %} api/tests{% endif %}

addopts =
    -v
    --strict-markers
    --tb=short
    --maxfail=1
    {% if use_allure %}--alluredir=allure-results{% endif %}
    {% if parallel_execution %}--numprocesses=auto{% endif %}
    {% if flaky_retry %}--reruns=2 --reruns-delay=1{% endif %}

markers =
    smoke: Quick smoke tests
    regression: Full regression suite
    ui: UI tests (Selenium or Playwright)
    {% if use_api_testing %}api: API tests{% endif %}
    {% if use_selenium %}selenium: Selenium-specific tests{% endif %}
    {% if use_playwright %}playwright: Playwright-specific tests{% endif %}

{% if use_playwright %}
asyncio_mode = auto
{% endif %}
```

---

### 4.6 Quality Tools Integration

#### 4.6.1 Makefile Targets

**Generated Makefile**:
```makefile
.PHONY: help install test {% if use_quality_tools %}format lint typecheck{% endif %}

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt
	{% if use_playwright %}playwright install{% endif %}

test:  ## Run all tests
	pytest tests/ -v

{% if use_selenium %}
test-selenium:  ## Run Selenium tests only
	pytest tests/ -m selenium -v
{% endif %}

{% if use_playwright %}
test-playwright:  ## Run Playwright tests only
	pytest tests_pw/ -v
{% endif %}

{% if use_docker %}
test-local:  ## Run with local Selenium Grid
	docker-compose -f docker/docker-compose.local.yml up -d
	./docker/wait-for-grid.sh
	HUB=http://localhost:4444/wd/hub pytest tests/ -v
	docker-compose -f docker/docker-compose.local.yml down
{% endif %}

{% if use_allure %}
test-allure:  ## Run tests with Allure reporting
	pytest --alluredir=allure-results
	allure serve allure-results
{% endif %}

{% if use_quality_tools %}
format:  ## Format code with black and isort
	black .
	isort .

format-check:  ## Check formatting without changes
	black --check .
	isort --check .

lint:  ## Lint with flake8
	flake8 .

typecheck:  ## Type check with mypy
	mypy pages/ tests/

quality:  ## Run all quality checks
	make format-check
	make lint
	make typecheck
{% endif %}
```

#### 4.6.2 Pre-commit Hooks (if enabled)

**`.pre-commit-config.yaml`**:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

---

### 4.7 Docker Support

#### 4.7.1 Docker Compose Configuration

**docker/docker-compose.local.yml** (Selenium Grid for local development):
```yaml
version: '3.8'

services:
  selenium-hub:
    image: selenium/hub:latest
    ports:
      - "4444:4444"
    environment:
      GRID_MAX_SESSION: 5
      GRID_BROWSER_TIMEOUT: 300

  {% for browser in browsers %}
  {{ browser }}-node:
    image: selenium/node-{{ browser }}:latest
    depends_on:
      - selenium-hub
    environment:
      SE_EVENT_BUS_HOST: selenium-hub
      SE_EVENT_BUS_PUBLISH_PORT: 4442
      SE_EVENT_BUS_SUBSCRIBE_PORT: 4443
      SE_NODE_MAX_SESSIONS: 2
    shm_size: 2gb
  {% endfor %}
```

**docker/wait-for-grid.sh** (health check script):
```bash
#!/bin/bash
set -e

echo "Waiting for Selenium Grid to be ready..."

until curl -sSL http://localhost:4444/status | jq -r '.value.ready' | grep -q "true"; do
    echo "Grid not ready yet, waiting..."
    sleep 2
done

echo "Selenium Grid is ready!"
```

---

### 4.8 CI/CD Integration

**`.github/workflows/test.yml`**:
```yaml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  {% if use_quality_tools %}
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run quality checks
        run: make quality
  {% endif %}

  {% if use_selenium %}
  selenium-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: {{ browsers }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Start Selenium Grid
        run: docker-compose -f docker/docker-compose.local.yml up -d
      - name: Wait for Grid
        run: ./docker/wait-for-grid.sh
      - name: Run tests
        run: |
          HUB=http://localhost:4444/wd/hub \
          BROWSER=${{ matrix.browser }} \
          pytest tests/ -v
      - name: Upload Allure results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: allure-results-${{ matrix.browser }}
          path: allure-results/
  {% endif %}

  {% if use_playwright %}
  playwright-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install --with-deps
      - name: Run Playwright tests
        run: pytest tests_pw/ -v
  {% endif %}
```

---

## 5. Implementation Plan

### 5.1 Phase 1: Core Scaffolding (MVP)
**Goal**: Users can generate working Selenium OR Playwright projects

**Tasks**:
1. ✅ Set up project structure with Poetry
2. ✅ Implement Click CLI framework with `init` command
3. ✅ Create questionary-based interactive prompts
4. ✅ Build Jinja2 template system
5. ✅ Create Selenium templates (base_page, locators, example test)
6. ✅ Create Playwright templates (async base_page, example test)
7. ✅ Implement ProjectGenerator class
8. ✅ Add pytest.ini, requirements.txt generation
9. ✅ Generate basic README.md
10. ✅ Write unit tests for generators

**Acceptance Criteria**:
- User can run `qfg init my-tests --driver selenium`
- Generated project has working example test
- `pytest tests/test_login.py -v` passes

### 5.2 Phase 2: Feature Expansion
**Goal**: Add optional features (Docker, CI/CD, quality tools)

**Tasks**:
1. ✅ Add Docker template generation
2. ✅ Add GitHub Actions workflow generation
3. ✅ Add quality tool configs (black, flake8, mypy)
4. ✅ Add pre-commit hook configuration
5. ✅ Add Allure reporting integration
6. ✅ Create Makefile template
7. ✅ Implement "both drivers" mode (duplicate tests)
8. ✅ Add API testing templates (if enabled)

**Acceptance Criteria**:
- User can enable/disable each feature via prompts
- Docker compose generates correctly for selected browsers
- CI workflow runs all selected test suites

### 5.3 Phase 3: Code Generation Commands
**Goal**: Users can extend generated projects

**Tasks**:
1. ✅ Implement `qfg add-page` command
2. ✅ Implement `qfg add-test` command
3. ✅ Implement `qfg config` command
4. ✅ Implement `qfg validate` command
5. ✅ Create PageObjectGenerator class
6. ✅ Create TestGenerator class
7. ✅ Add conftest.py fixture auto-updates (optional)

**Acceptance Criteria**:
- `qfg add-page inventory` creates page object + locator enum
- `qfg add-test checkout` creates test file with boilerplate
- `qfg validate` catches structural issues

### 5.4 Phase 4: Documentation & Polish
**Goal**: Users can understand and extend the framework

**Tasks**:
1. ✅ Write comprehensive README with tutorials
2. ✅ Document template customization
3. ✅ Create troubleshooting guide
4. ✅ Add inline code comments in templates
5. ✅ Create CONTRIBUTING.md
6. ✅ Add example extension scenarios
7. ✅ Write integration tests (generate → run tests)
8. ✅ Add CLI `--help` text for all commands

**Acceptance Criteria**:
- README covers installation → first project → customization
- Users can override templates successfully
- 80%+ test coverage on framework code

### 5.5 Phase 5: Workspace & Advanced Features (Future)
**Goal**: Multi-project management and upgrades

**Tasks**:
- ⏳ Implement workspace initialization
- ⏳ Add `qfg upgrade` command
- ⏳ Create template versioning system
- ⏳ Add preset bundles (minimal/standard/full)
- ⏳ Support custom plugins

---

## 6. Technical Decisions & Rationale

### 6.1 Why Click over argparse?
- **Pro**: Better support for nested commands, automatic help generation
- **Pro**: Industry standard (used by Flask, AWS CLI)
- **Con**: Extra dependency (acceptable for CLI tool)

### 6.2 Why questionary over raw input()?
- **Pro**: Better UX with validation, multi-select, autocomplete
- **Pro**: Consistent styling and error handling
- **Con**: Extra dependency (acceptable for interactive tool)

### 6.3 Why Jinja2 over f-strings?
- **Pro**: Supports conditionals (`{% if %}`) and loops in templates
- **Pro**: Template inheritance reduces duplication
- **Pro**: Industry standard for Python templating
- **Con**: Learning curve for non-Jinja users (mitigated by simple syntax)

### 6.4 Why YAML for config?
- **Pro**: Human-readable with comments
- **Pro**: Widely used in CI/CD (GitHub Actions, Docker Compose)
- **Con**: YAML parsing quirks (use `safe_load()` to mitigate)

### 6.5 Why Python 3.11+?
- **Pro**: Modern type hints (`Self`, `TypedDict`)
- **Pro**: Better performance (10-60% faster than 3.9)
- **Pro**: Pattern matching for validation logic
- **Con**: Requires users to upgrade (acceptable for new tool in 2025)

### 6.6 Why duplicate tests for "both" mode?
- **Pro**: Simpler architecture (no abstraction layer needed)
- **Pro**: Users can see driver-specific patterns clearly
- **Pro**: Easier to maintain separate test suites
- **Con**: Code duplication (acceptable trade-off for clarity)

### 6.7 Why async Playwright?
- **Pro**: Modern best practice for Playwright
- **Pro**: Better performance with parallel execution
- **Pro**: Future-proof (async is Python's direction)
- **Con**: Steeper learning curve (mitigated by examples)

---

## 7. Dependencies

### 7.1 Framework Dependencies (qa-framework-gen itself)

**Core**:
- `click>=8.1.0` - CLI framework
- `questionary>=2.0.0` - Interactive prompts
- `jinja2>=3.1.0` - Template rendering
- `pyyaml>=6.0` - Configuration parsing
- `structlog>=24.0.0` - Logging

**Development**:
- `pytest>=7.4.0` - Testing framework
- `pytest-cov>=4.1.0` - Coverage reporting
- `black>=24.0.0` - Code formatting
- `mypy>=1.8.0` - Type checking
- `poetry>=1.7.0` - Dependency management

### 7.2 Generated Project Dependencies

**Always Included**:
```
pytest>=7.4.0
pytest-html>=4.1.0
python-dotenv>=1.0.0
```

**If Selenium selected**:
```
selenium>=4.16.0
webdriver-manager>=4.0.1
```

**If Playwright selected**:
```
pytest-playwright>=0.4.4
playwright>=1.40.0
pytest-asyncio>=0.23.0
```

**If Allure selected**:
```
allure-pytest>=2.13.0
```

**If Quality Tools selected**:
```
black>=24.0.0
flake8>=7.0.0
mypy>=1.8.0
bandit>=1.7.6
isort>=5.13.0
```

**If Parallel Execution selected**:
```
pytest-xdist>=3.5.0
```

**If Flaky Retry selected**:
```
pytest-rerunfailures>=13.0
```

**If API Testing selected**:
```
requests>=2.31.0
```

---

## 8. Testing Strategy

### 8.1 Unit Tests
**Target**: Individual functions and classes

**Examples**:
- `test_validators.py`: Test URL validation, project name validation
- `test_generators.py`: Test template rendering with different configs
- `test_prompts.py`: Test questionary prompt logic

### 8.2 Integration Tests
**Target**: End-to-end project generation

**Examples**:
- `test_project_generation.py`:
  ```python
  def test_selenium_project_generation(tmp_path):
      """Generate Selenium project and verify structure."""
      generator = ProjectGenerator(
          project_name="test-project",
          driver="selenium",
          base_url="https://example.com",
          output_dir=tmp_path
      )
      generator.generate()

      assert (tmp_path / "test-project" / "pages" / "base_page.py").exists()
      assert (tmp_path / "test-project" / "tests" / "test_login.py").exists()
  ```

### 8.3 Snapshot Tests
**Target**: Generated file content accuracy

**Examples**:
- Compare generated `pytest.ini` against known-good snapshot
- Verify Makefile contains expected targets

### 8.4 CLI Tests
**Target**: Click command invocations

**Examples**:
```python
from click.testing import CliRunner

def test_init_command_no_interactive():
    """Test qfg init with --no-interactive flag."""
    runner = CliRunner()
    result = runner.invoke(cli, ['init', 'my-project', '--no-interactive'])

    assert result.exit_code == 0
    assert "Project created successfully" in result.output
```

---

## 9. Documentation Outline

### 9.1 README.md Structure

```markdown
# QA Framework Generator (qa-framework-gen)

Scaffold production-ready pytest automation projects in seconds.

## Features
- 🚀 Quick project setup with interactive CLI
- 🔧 Selenium WebDriver + Playwright support
- 📦 Docker & CI/CD ready
- ✨ Page Object Model with typed locators
- 📊 Allure reporting integration
- 🛠️ Code quality tools pre-configured

## Installation

### Prerequisites
- Python 3.11 or higher
- pip 23.0+
- Git 2.30+

### Recommended: Install with pipx (Isolated Installation)

The best way to install `qa-framework-gen` is using [pipx](https://pypa.github.io/pipx/), which installs CLI tools in isolated environments:

```bash
# Install pipx if you don't have it
pip install pipx
pipx ensurepath

# Install qa-framework-gen from GitHub
pipx install git+https://github.com/navinislam/qa-framework-gen.git

# Verify installation
qfg --version
qfg --help
```

**Why pipx?**
- ✅ Installs in isolated environment (no dependency conflicts)
- ✅ `qfg` command available globally across all projects
- ✅ Easy upgrades: `pipx upgrade qa-framework-gen`
- ✅ Industry best practice for Python CLI tools

### Alternative: Direct pip Installation

```bash
# Install directly with pip
pip install git+https://github.com/navinislam/qa-framework-gen.git

# Verify installation
qfg --version
```

**Note**: This installs into your current Python environment. Consider using a virtual environment to avoid conflicts.

### For Contributors: Editable Installation

```bash
# Clone the repository
git clone https://github.com/navinislam/qa-framework-gen.git
cd qa-framework-gen

# Install in editable mode
pip install -e .

# Or with Poetry
poetry install

# Verify installation
qfg --version
```

### Upgrading

**With pipx**:
```bash
pipx upgrade qa-framework-gen
```

**With pip**:
```bash
pip install --upgrade git+https://github.com/navinislam/qa-framework-gen.git
```

## Quick Start

### Create Your First Project
```bash
qfg init my-tests
# Answer interactive prompts
cd my-tests
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

### Add a New Page Object
```bash
qfg add-page inventory --url /inventory
# Edit pages/inventory_page.py
```

### Add a New Test
```bash
qfg add-test checkout
# Edit tests/test_checkout.py
```

## Tutorial: Building a Complete Test Suite

### Step 1: Initialize Project
[Detailed walkthrough with screenshots/terminal output]

### Step 2: Understand Generated Structure
[Explanation of each directory and file]

### Step 3: Add Your First Custom Page
[Complete example of adding inventory page]

### Step 4: Write Your First Test
[Complete example of checkout test]

### Step 5: Run Tests Locally
[Using Makefile, pytest commands]

### Step 6: Run Tests in Docker
[Docker Compose commands]

### Step 7: Set Up CI/CD
[GitHub Actions configuration]

## Customization Guide

### Extending BaseFactory (Selenium)
```python
# pages/base_page.py
class BaseFactory:
    def wait_for_ajax(self):
        """Custom wait for AJAX completion."""
        # Your implementation
```

### Overriding Templates
[How to create .framework/templates/ for custom generation]

### Adding Custom Fixtures
[Examples of conftest.py patterns]

### Integrating Third-Party Libraries
[How to add things like Faker, pytest-bdd]

## Best Practices

### Page Object Patterns
- One page object per URL/view
- Use typed locators (Locator dataclass)
- Keep business logic in page objects, not tests

### Test Organization
- Group related tests in classes
- Use pytest markers for categorization
- Parametrize data-driven tests

### Naming Conventions
- Page objects: `{page_name}_page.py` (snake_case)
- Tests: `test_{feature}.py`
- Fixtures: Descriptive names matching page objects

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'pages'`
**Solution**: Run pytest from project root, or set PYTHONPATH

**Issue**: Selenium Grid not ready
**Solution**: Ensure `wait-for-grid.sh` completes before running tests

**Issue**: Playwright browser not found
**Solution**: Run `playwright install`

### Getting Help
- GitHub Issues: [link]
- Discussions: [link]

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - See [LICENSE](LICENSE)
```

### 9.2 In-Code Documentation

**Template Comments**:
```jinja2
{#
  This template generates the base page object for Selenium.
  Variables:
    - project_name: Name of the test project
    - base_url: Application base URL

  Customization:
    - Add custom wait methods below wait_for_element_clickable()
    - Override __init__() to add project-specific setup
#}
```

**Generated Code Comments**:
```python
class BaseFactory:
    """
    Base page factory with resilient waits and logging.

    All page objects should inherit from this class to get:
    - Automatic screenshot capture on failures
    - Configurable retry logic for waits
    - Structlog-based logging

    Example:
        class LoginPage(BaseFactory):
            def __init__(self, base_factory):
                super().__init__(base_factory.driver)
    """
```

---

## 10. Future Enhancements (Post-MVP)

### 10.1 Framework Upgrades
- `qfg upgrade` command with safe merging
- Semantic versioning for templates
- Change logs for framework updates

### 10.2 Preset Bundles
- `--template minimal`: Basic setup (no Docker, no quality tools)
- `--template standard`: Docker + CI/CD
- `--template full`: Everything enabled

### 10.3 Plugin System
```python
# Custom generator plugin
class CustomPageGenerator(PageObjectGenerator):
    def generate(self):
        # Custom logic
        pass

# Register in .framework/plugins/
```

### 10.4 Cloud Integrations
- BrowserStack configuration
- Sauce Labs support
- LambdaTest integration

### 10.5 Advanced Reporting
- Custom Allure categories
- Slack/Teams notifications
- Historical trend analysis

### 10.6 Visual Regression (when requested)
- Playwright screenshot comparison
- Percy.io integration
- Applitools Eyes support

---

## 11. Non-Functional Requirements

### 11.1 Performance
- Project generation completes in < 5 seconds
- CLI startup time < 1 second
- Template rendering handles 100+ files efficiently

### 11.2 Maintainability
- 80%+ test coverage on framework code
- Type hints on all public APIs
- Docstrings for all classes and methods

### 11.3 Usability
- Interactive prompts provide validation feedback immediately
- Error messages include actionable suggestions
- `--help` text explains all options clearly

### 11.4 Compatibility
- Works on macOS and Linux (Ubuntu, Fedora, Debian)
- Python 3.11+ required
- Git 2.30+ recommended (for workspace features)

---

## 12. Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Template bugs generate broken projects | High | Medium | Integration tests, snapshot tests |
| Jinja2 syntax errors in templates | Medium | Low | Linting templates, unit tests |
| Dependency conflicts in requirements.txt | Medium | Medium | Pin versions, use Poetry's resolver |
| Users modify generated code, break framework | Low | High | Clear documentation on safe customization |
| Framework upgrades break existing projects | High | Medium | Versioning, careful change management |

---

## 13. Success Metrics

### 13.1 Adoption Metrics (Post-Launch)
- GitHub stars/forks
- Number of generated projects (if telemetry added)
- Community contributions (PRs, issues)

### 13.2 Quality Metrics
- Test coverage: 80%+
- Zero critical bugs in first release
- < 5% issue rate on generated projects

### 13.3 Developer Experience Metrics
- Time to first working test: < 5 minutes
- Documentation clarity: User feedback
- Customization success rate: Track via discussions

---

## 14. Open Questions & Decisions Needed

### 14.1 Resolved
- ✅ Package name: `qa-framework-gen`
- ✅ Separate repository
- ✅ Target Python 3.11+
- ✅ Async Playwright
- ✅ Duplicate tests for "both" mode
- ✅ Environment variables for sensitive data

### 14.2 Deferred to Implementation
- Template override discovery mechanism
- Workspace upgrade strategy
- Plugin system API design

---

## 15. Glossary

- **POM**: Page Object Model - design pattern for test automation
- **Locator**: Tuple of (strategy, value) for finding elements (e.g., `(By.ID, "username")`)
- **BaseFactory**: Core class providing wait helpers and logging
- **Fixture**: Pytest concept for reusable test setup/teardown
- **Conftest**: Special pytest file (`conftest.py`) for shared fixtures
- **Marker**: Pytest decorator for categorizing tests (`@pytest.mark.smoke`)
- **Parametrize**: Pytest feature for data-driven testing

---

## 16. Approval & Next Steps

**This spec requires user approval before implementation.**

**Review Checklist**:
- [ ] Scope matches user expectations (new projects only, no migration)
- [ ] CLI commands make sense (`init`, `add-page`, `add-test`, `config`, `validate`)
- [ ] Template structure is clear and extensible
- [ ] Example tests demonstrate framework capabilities
- [ ] Documentation outline covers user needs
- [ ] Implementation phases are realistic

**Once approved**, type **'GO!'** to begin Phase 1: Core Scaffolding.

**Expected Timeline** (rough estimates):
- Phase 1 (Core): 2-3 days
- Phase 2 (Features): 2-3 days
- Phase 3 (Commands): 1-2 days
- Phase 4 (Docs): 1-2 days
- **Total**: ~1-2 weeks for MVP

**First Implementation Step**:
Create separate repository structure and scaffold CLI with `qfg init` command.
