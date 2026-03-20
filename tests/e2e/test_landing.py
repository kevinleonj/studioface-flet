"""E2E tests for the landing page."""

import pytest

pytestmark = pytest.mark.skipif(
    True,
    reason="E2E tests require Playwright browser and running server. Run manually.",
)


def test_landing_loads(app_server):
    """Landing page loads without errors."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(app_server)
        assert "StudioFace" in page.title()
        browser.close()


def test_hero_visible(app_server):
    """Hero section with CTA is visible."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(app_server)
        page.wait_for_timeout(3000)
        content = page.content()
        assert "Professional" in content or "Headshot" in content
        browser.close()
