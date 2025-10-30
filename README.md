# qa-framework-gen

CLI tool to generate pytest automation frameworks with Selenium and/or Playwright support.

## Features

- 🎯 **Interactive CLI**: Questionary-powered prompts for easy project setup
- 🔧 **Flexible Driver Support**: Choose Selenium, Playwright, or both
- 📦 **Feature Selection**: Pick and choose components (Docker, CI/CD, Allure, etc.)
- 🏗️ **Page Object Model**: Auto-generate page objects and tests
- ⚙️ **Config-Aware**: Commands read from `.framework-config.yml` for smart defaults
- 📝 **Best Practices**: Quality tools, pre-commit hooks, and proper project structure

## Installation

### Recommended: pipx (isolated installation)

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

### Alternative: pip install from source

```bash
# Clone the repository
git clone https://github.com/navinislam/qa-framework-gen.git
cd qa-framework-gen

# Install in editable mode
pip install -e .

# Or install normally
pip install .
```

## Quick Start

### 1. Create a New Project

```bash
qfg init
```

You'll be prompted for:
- Project name
- Base URL
- Driver selection (Selenium, Playwright, or Both)
- Browser support
- Features (Docker, CI/CD, Allure, Quality Tools, etc.)

Example session:
```
🎯 QA Framework Generator

? Project name: my-automation-tests
? Base URL: https://www.saucedemo.com
? Which driver(s) do you want to use? Both (Selenium + Playwright)
? Select browsers to support: chrome, firefox
? Select features to include:
  ✓ Docker Compose (Selenium Grid)
  ✓ CI/CD (GitHub Actions)
  ✓ Allure Reporting
  ✓ Quality Tools (black, flake8, mypy, bandit)
  ✓ Pre-commit Hooks
  ✓ Parallel Execution (pytest-xdist)

✅ Project 'my-automation-tests' created successfully!
```

### 2. Set Up the Generated Project

```bash
cd my-automation-tests
pip install -r requirements.txt

# If using Playwright
playwright install
```

### 3. Add Page Objects

```bash
# Add a login page object
qfg add-page login --url /login

# The command reads driver type from .framework-config.yml
# If both drivers are configured, you'll be prompted to choose
```

### 4. Add Tests

```bash
# Add a login test
qfg add-test login

# For API tests (if enabled)
qfg add-test users --type api
```

### 5. Run Tests

```bash
# Run all tests
pytest

# Run with parallel execution
pytest -n auto

# Run specific markers
pytest -m smoke
pytest -m selenium
pytest -m playwright
```

## CLI Commands

### `qfg init`

Initialize a new automation framework project with interactive prompts.

**Options:**
- `--name TEXT`: Project name (prompted if not provided)
- `--base-url TEXT`: Base URL for the application under test
- `-d, --directory PATH`: Directory where the project will be created (default: current directory)
- `-f, --force`: Overwrite existing directory if not empty

**Example:**
```bash
qfg init --name my-tests --base-url https://example.com
```

### `qfg add-page PAGE_NAME`

Add a new page object to the project. Automatically reads configuration from `.framework-config.yml`.

**Arguments:**
- `PAGE_NAME`: Name of the page (e.g., "login", "dashboard")

**Options:**
- `--url TEXT`: URL path for the page (e.g., `/login`)
- `--driver [selenium|playwright|both]`: Driver type (auto-detected from config if not specified)

**Behavior:**
- Reads `.framework-config.yml` to determine driver type and base URL
- Only prompts for driver if config shows "both" drivers
- Automatically generates page objects with proper structure

**Example:**
```bash
# Auto-detects driver from config
qfg add-page login --url /login

# Explicit driver selection
qfg add-page dashboard --url /dashboard --driver selenium
```

### `qfg add-test TEST_NAME`

Add a new test file to the project. Automatically reads configuration from `.framework-config.yml`.

**Arguments:**
- `TEST_NAME`: Name of the test (e.g., "login", "checkout")

**Options:**
- `--type [ui|api]`: Test type (prompted if not provided)
- `--driver [selenium|playwright|both]`: Driver type for UI tests

**Behavior:**
- Reads `.framework-config.yml` to determine driver type and API testing status
- Only prompts for driver if config shows "both" drivers
- Only offers API option if enabled in config

**Example:**
```bash
# Auto-detects settings from config
qfg add-test login

# Explicit test type
qfg add-test users --type api
```

## Project Structure

### Selenium Only
```
my-tests/
├── .framework-config.yml    # Project configuration
├── pytest.ini               # Pytest configuration
├── requirements.txt         # Python dependencies
├── pages/                   # Page objects
│   ├── __init__.py
│   └── login_page.py
├── tests/                   # Test files
│   ├── __init__.py
│   ├── test_login.py
│   └── data/               # Test data
└── README.md
```

### Both Drivers
```
my-tests/
├── .framework-config.yml
├── pytest.ini
├── requirements.txt
├── pages/                   # Selenium page objects
│   ├── __init__.py
│   └── login_page.py
├── pages_pw/               # Playwright page objects
│   ├── __init__.py
│   └── login_page.py
├── tests/                  # Selenium tests
│   ├── __init__.py
│   └── test_login.py
├── tests_pw/              # Playwright tests
│   ├── __init__.py
│   └── test_login_pw.py
└── README.md
```

## Configuration File

The `.framework-config.yml` file stores project settings:

```yaml
framework:
  version: "1.0.0"
  generator: "qa-framework-gen"
  created: "2025-10-29T22:00:00"

project:
  name: "my-tests"
  base_url: "https://www.saucedemo.com"

driver:
  type: "both"  # selenium, playwright, or both
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
  flaky_retry: false
  api_testing: false

settings:
  logging_mode: "json"
  test_data_format: "yaml"
  playwright_async: true
```

## Available Features

### Docker Compose
Generates `docker-compose.yml` for Selenium Grid with hub and browser nodes.

### CI/CD (GitHub Actions)
Creates `.github/workflows/test.yml` with:
- Quality checks (black, flake8, mypy, bandit)
- Test matrix across browsers
- Allure report generation

### Allure Reporting
Adds allure-pytest dependency and report generation commands.

### Quality Tools
Includes:
- **black**: Code formatting
- **flake8**: Linting with plugins (docstrings, bugbear, comprehensions)
- **mypy**: Type checking
- **bandit**: Security scanning

### Pre-commit Hooks
Generates `.pre-commit-config.yaml` with automated quality checks.

### Parallel Execution
Adds pytest-xdist for running tests in parallel (`pytest -n auto`).

### Flaky Test Retry
Includes pytest-retry for handling flaky tests.

### API Testing
Adds requests library and API test templates.

## Extending the Framework

### Custom Page Objects

Selenium page objects inherit structure:
```python
class LoginPage:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.url = "https://example.com/login"

    def visit(self) -> None:
        self.driver.get(self.url)
```

Playwright page objects (async):
```python
class LoginPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.url = "https://example.com/login"

    async def visit(self) -> None:
        await self.page.goto(self.url)
```

### Custom Test Templates

Modify generated tests by editing the `_create_*_test()` functions in `framework/cli/__init__.py`.

### Adding More Features

To add custom features to generated projects:
1. Update the feature selection in the `init` command
2. Add conditional logic in project generation
3. Update requirements.txt generation
4. Create corresponding template files

## Development

### Setup Development Environment

```bash
git clone https://github.com/navinislam/qa-framework-gen.git
cd qa-framework-gen

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run quality checks
black framework --check
flake8 framework
mypy framework
```

### Running the CLI Locally

```bash
# Run as module
python -m framework.cli init

# Or use the installed command
qfg init
```

## Python Version

Requires Python 3.11 or higher.

## License

MIT

## Author

Navin Islam

## Contributing

Contributions welcome! Please open an issue or pull request on GitHub.

## Roadmap

- [ ] Template customization via config files
- [ ] Support for additional testing frameworks (unittest, nose)
- [ ] Visual regression testing integration (Percy, Applitools)
- [ ] Database testing utilities
- [ ] Performance testing support (Locust integration)
- [ ] Mobile testing (Appium support)
- [ ] Cloud grid integration (BrowserStack, Sauce Labs)