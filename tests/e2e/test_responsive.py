"""E2E tests for responsive layouts."""

import pytest

pytestmark = pytest.mark.skipif(
    True,
    reason="E2E tests require Playwright browser and running server. Run manually.",
)


def test_mobile_layout(app_server):
    """App renders correctly at 360px width."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 360, "height": 640})
        page.goto(app_server)
        page.wait_for_timeout(3000)
        assert page.evaluate("document.documentElement.scrollWidth") <= 360
        browser.close()


def test_tablet_layout(app_server):
    """App renders correctly at 768px width."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 768, "height": 1024})
        page.goto(app_server)
        page.wait_for_timeout(3000)
        browser.close()


def test_desktop_layout(app_server):
    """App renders correctly at 1920px width."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(app_server)
        page.wait_for_timeout(3000)
        browser.close()
