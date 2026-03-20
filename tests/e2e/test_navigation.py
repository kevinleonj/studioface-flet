"""E2E tests for navigation between pages."""

import pytest

pytestmark = pytest.mark.skipif(
    True,
    reason="E2E tests require Playwright browser and running server. Run manually.",
)


def test_all_routes_accessible(app_server):
    """Every route returns a valid page (no crash)."""
    from playwright.sync_api import sync_playwright

    routes = ["/", "/login", "/create", "/gallery", "/payment/success", "/nonexistent"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for route in routes:
            page.goto(f"{app_server}{route}")
            page.wait_for_timeout(2000)
            content = page.content()
            assert "Traceback" not in content
        browser.close()


def test_404_page(app_server):
    """Unknown routes show 404 page."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"{app_server}/this-does-not-exist")
        page.wait_for_timeout(2000)
        content = page.content()
        assert "404" in content or "not found" in content.lower()
        browser.close()
