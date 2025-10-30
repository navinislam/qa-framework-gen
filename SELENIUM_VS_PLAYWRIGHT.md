# Selenium BaseFactory vs Playwright - Method Comparison

## Overview
This document maps Selenium BaseFactory methods to their Playwright equivalents and suggests improvements for both base page implementations.

---

## Method Comparison Table

| Selenium Method | Playwright Equivalent | Notes |
|----------------|----------------------|-------|
| **Navigation** |
| `open(path)` | `page.goto(url)` | Already in PlaywrightBasePage as `navigate_to()` |
| **Waits** |
| `wait_for_element_present()` | `locator.wait_for(state="attached")` | Playwright auto-waits by default |
| `wait_for_element_visible()` | `locator.wait_for(state="visible")` | Already in template as `wait_for_selector()` |
| `wait_for_element_clickable()` | Built-in to `click()` | Playwright auto-waits for actionability |
| `wait_for_text_to_be_present()` | `expect(locator).to_contain_text()` | Use playwright assertions |
| **Element Actions** |
| `click_element()` | `locator.click()` | Already in template as `click()` |
| `send_keys_to_element()` | `locator.fill()` or `locator.type()` | Already in template as `fill()` |
| `clear_element_text()` | `locator.clear()` | Simple one-liner in Playwright |
| **Element State Checks** |
| `is_element_present()` | `locator.count() > 0` | Check element count |
| `is_element_displayed()` | `locator.is_visible()` | Already in template |
| `is_element_enabled()` | `locator.is_enabled()` | Already in template |
| **Element Attributes** |
| `get_text_from_element()` | `locator.text_content()` | Already in template as `get_text()` |
| `get_attribute_value()` | `locator.input_value()` | Get input field value |
| `get_attribute_size()` | `locator.bounding_box()['width']` | Get element dimensions |
| **Screenshots** |
| `generate_screenshot()` | `page.screenshot()` | Already in template as `take_screenshot()` |
| `quit_driver()` | `page.close()` or `context.close()` | Handled by pytest fixtures |

---

## Missing Functions Analysis

### Selenium BasePage (Generated) Missing from BaseFactory

#### Critical Infrastructure (Should Add):
1. ✅ **`_wait_with_retry()`** - Resilient retry pattern with auto-screenshots
2. ✅ **`_logger()`** - Structured logging (requires structlog dependency)
3. ✅ **`_resolve_locator()`** - Support for Locator dataclass (if using locator model)
4. ✅ **`_locator_repr()`** - Human-readable logging

#### Useful Helpers (Recommended):
5. ⚠️ **`wait_for_text_to_be_present()`** - Common use case
6. ⚠️ **`is_element_present()`** - Check existence without throwing
7. ⚠️ **`is_element_enabled()`** - Check enabled state
8. ⚠️ **`get_attribute_value()`** - Get input values
9. ⚠️ **`clear_element_text()`** - Clear with backspace (some inputs need this)

#### Optional (Nice to Have):
10. ⏹️ **`get_attribute_size()`** - For layout testing
11. ⏹️ **`click_element_and_hold()`** - Special click behavior
12. ⏹️ **`send_keys_to_element(submit=True, sensitive=True)`** - Advanced options

---

## Playwright BasePage Suggestions

### Missing Methods (Should Add):

```python
async def is_present(self, selector: str) -> bool:
    """Check if element exists in DOM (doesn't need to be visible)."""
    return await self.get_element(selector).count() > 0

async def get_attribute(self, selector: str, attribute: str) -> str | None:
    """Get any attribute from an element."""
    return await self.get_element(selector).get_attribute(attribute)

async def get_input_value(self, selector: str) -> str:
    """Get value from input field."""
    return await self.get_element(selector).input_value()

async def clear(self, selector: str) -> None:
    """Clear an input field."""
    await self.get_element(selector).clear()

async def press_key(self, selector: str, key: str) -> None:
    """Press a key on an element."""
    await self.get_element(selector).press(key)

async def select_option(self, selector: str, value: str) -> None:
    """Select option from dropdown."""
    await self.get_element(selector).select_option(value)

async def check(self, selector: str) -> None:
    """Check a checkbox."""
    await self.get_element(selector).check()

async def uncheck(self, selector: str) -> None:
    """Uncheck a checkbox."""
    await self.get_element(selector).uncheck()

async def hover(self, selector: str) -> None:
    """Hover over an element."""
    await self.get_element(selector).hover()

async def double_click(self, selector: str) -> None:
    """Double click an element."""
    await self.get_element(selector).dblclick()

async def get_all_text_contents(self, selector: str) -> list[str]:
    """Get text from all matching elements."""
    return await self.get_element(selector).all_text_contents()

async def wait_for_url(self, url_pattern: str, timeout: int = 30000) -> None:
    """Wait for URL to match pattern."""
    await self.page.wait_for_url(url_pattern, timeout=timeout)

async def reload(self) -> None:
    """Reload the current page."""
    await self.page.reload()

async def go_back(self) -> None:
    """Navigate back in browser history."""
    await self.page.go_back()

async def go_forward(self) -> None:
    """Navigate forward in browser history."""
    await self.page.go_forward()
```

---

## Recommendations

### For Selenium BasePage Enhancement:

1. **Add retry logic pattern** from BaseFactory
2. **Add structured logging** (optional, but highly valuable)
3. **Add common helpers**: `is_element_present()`, `is_element_enabled()`, `get_attribute_value()`
4. **Add text waiting**: `wait_for_text_to_be_present()`
5. **Consider Locator dataclass support** if users want type safety

### For Playwright BasePage Enhancement:

1. **Add element existence check**: `is_present()`
2. **Add input helpers**: `get_input_value()`, `clear()`, `press_key()`
3. **Add form helpers**: `select_option()`, `check()`, `uncheck()`
4. **Add mouse actions**: `hover()`, `double_click()`
5. **Add navigation helpers**: `wait_for_url()`, `reload()`, `go_back()`
6. **Add attribute getter**: `get_attribute()`

### Priority Matrix:

**HIGH PRIORITY** (Add to both):
- ✅ `is_element_present()` / `is_present()` - Very common need
- ✅ `get_attribute_value()` / `get_input_value()` - Essential for form testing
- ✅ `wait_for_text_to_be_present()` / text assertions - Common wait condition

**MEDIUM PRIORITY**:
- ⚠️ `clear_element_text()` / `clear()` - Some sites need special clearing
- ⚠️ `hover()` - Needed for dropdown/tooltip testing
- ⚠️ `select_option()` - Dropdown handling
- ⚠️ Retry logic for Selenium (already excellent in BaseFactory)

**LOW PRIORITY**:
- ⏹️ `get_attribute_size()` - Layout testing (specialized)
- ⏹️ `double_click()` - Rarely needed
- ⏹️ Advanced click variants - Edge cases

---

## Key Differences: Selenium vs Playwright

### Selenium Needs Manual Work:
- Explicit waits required
- No auto-retry on stale elements
- Manual screenshot on failure
- More verbose locator syntax

### Playwright Has Built-in:
- Auto-waits for actionability
- Auto-retries on transient failures
- Better error messages with screenshots
- Simpler locator syntax (CSS/XPath strings)

### BaseFactory Excellence:
The `_wait_with_retry()` pattern in BaseFactory is **brilliant** for Selenium:
- Configurable retry attempts via env vars
- Automatic screenshot on final failure
- Structured logging with full context
- Works around Selenium's brittleness

**Recommendation**: Port the retry pattern concept to Playwright for edge cases where auto-wait isn't enough.

---

## Generated vs Reference Comparison

### What Generated BasePage is Missing:

**Infrastructure (Most Important)**:
1. No retry logic (`_wait_with_retry` pattern)
2. No structured logging
3. No Locator dataclass support
4. No automatic screenshot on wait failures

**Functionality**:
5. No `is_element_present()` check
6. No `is_element_enabled()` check
7. No `wait_for_text_to_be_present()`
8. No `get_attribute_value()`
9. No `clear_element_text()`
10. No submit option in `send_keys_to_element()`
11. No sensitive flag to hide passwords in logs

### Why These Matter:

- **Retry logic**: Makes tests more resilient to timing issues
- **Logging**: Makes debugging failures much easier
- **Screenshot on failure**: Instant visual debugging
- **Element state checks**: Avoid "element not found" vs "element not visible" confusion
- **Text waits**: Very common pattern in UI testing
- **Attribute getters**: Essential for validating form state

---

## Implementation Strategy

### Phase 1: Critical Infrastructure (Do First)
Add to generated Selenium BasePage:
```python
- _wait_with_retry() pattern
- is_element_present()
- is_element_enabled()
- wait_for_text_to_be_present()
- get_attribute_value()
```

Add to Playwright BasePage:
```python
- is_present()
- get_input_value()
- clear()
- select_option()
- hover()
```

### Phase 2: Nice to Have (Add Later)
- Structured logging for Selenium (requires structlog in requirements)
- Locator dataclass support (requires add-locators command)
- Advanced form helpers (check/uncheck, etc.)
- Mouse actions (double-click, right-click)

### Phase 3: Optional Enhancements
- Navigation helpers (go_back, reload)
- Multiple attribute getters
- Size/position getters
- Advanced wait conditions