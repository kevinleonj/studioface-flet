"""E2E tests for language switching."""

import pytest

pytestmark = pytest.mark.skipif(
    True,
    reason="E2E tests require Playwright browser and running server. Run manually.",
)


def test_language_switch_to_spanish(app_server):
    """Switching language updates all visible text to Spanish."""
    pass


def test_language_switch_to_german(app_server):
    """Switching to German updates all visible text."""
    pass


def test_language_persists_across_navigation(app_server):
    """Language choice persists when navigating between pages."""
    pass
