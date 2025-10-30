from __future__ import annotations

import allure


@allure.epic("Example")
@allure.feature("Smoke")
def test_example_smoke(base_page):
    """Placeholder smoke test; replace with project-specific checks."""
    assert base_page.driver.current_url.startswith("{{BASE_URL}}")
