"""Authentication service — login flows and token management."""

from typing import Any, Optional

import flet as ft

from app.services.api_client import StudioFaceAPI


async def login_with_magic_link(
    api: StudioFaceAPI, email: str, locale: str = "en"
) -> dict[str, Any]:
    """Request a magic link email.

    Args:
        api: API client instance.
        email: User's email address.
        locale: Language code for the email template.
    """
    return await api.send_magic_link(email, locale=locale)


async def login_with_microsoft(api: StudioFaceAPI) -> dict[str, Any]:
    """Get the Microsoft OAuth URL."""
    return await api.get_microsoft_auth_url()


async def handle_microsoft_callback(
    api: StudioFaceAPI, page: ft.Page, code: str, state: str
) -> dict[str, Any]:
    """Exchange Microsoft OAuth code for tokens and store them.

    Args:
        api: API client instance.
        page: Flet page for storage.
        code: Authorization code from Microsoft redirect.
        state: State parameter for CSRF verification.
    """
    result = await api.microsoft_callback(code, state)
    if "error" not in result:
        _store_auth_result(api, page, result)
    return result


async def verify_and_store_token(
    api: StudioFaceAPI, page: ft.Page, token: str
) -> dict[str, Any]:
    """Verify a magic-link token and store auth tokens on success."""
    result = await api.verify_token(token)
    if "error" not in result:
        _store_auth_result(api, page, result)
    return result


def _store_auth_result(api: StudioFaceAPI, page: ft.Page, result: dict[str, Any]) -> None:
    """Store auth tokens from a successful login/verify response.

    The backend may return tokens as:
      - access_token + refresh_token (standard OAuth)
      - token (legacy magic link response)
    """
    access_token = result.get("access_token", result.get("token", ""))
    refresh_token = result.get("refresh_token", "")

    if access_token:
        api.set_tokens(access_token, refresh_token)
        page.session.set("sf_access_token", access_token)
        if refresh_token:
            page.session.set("sf_refresh_token", refresh_token)
        page.session.set("user", result.get("user", result))

        # Register callback to persist refreshed tokens
        def on_refreshed(new_access: str, new_refresh: str) -> None:
            page.session.set("sf_access_token", new_access)
            page.session.set("sf_refresh_token", new_refresh)

        api.on_tokens_refreshed(on_refreshed)


async def restore_session(api: StudioFaceAPI, page: ft.Page) -> Optional[dict[str, Any]]:
    """Try to restore a session from stored tokens."""
    access_token = page.session.get("sf_access_token")
    if not access_token:
        return None

    refresh_token = page.session.get("sf_refresh_token") or ""
    api.set_tokens(access_token, refresh_token)

    # Register callback for auto-refresh persistence
    def on_refreshed(new_access: str, new_refresh: str) -> None:
        page.session.set("sf_access_token", new_access)
        page.session.set("sf_refresh_token", new_refresh)

    api.on_tokens_refreshed(on_refreshed)

    result = await api.get_current_user()
    if "error" in result:
        api.clear_tokens()
        page.session.remove("sf_access_token")
        page.session.remove("sf_refresh_token")
        return None
    page.session.set("user", result)
    return result


async def logout(api: StudioFaceAPI, page: ft.Page) -> None:
    """Log out: invalidate tokens on server and clear local state."""
    refresh_token = page.session.get("sf_refresh_token")
    await api.logout(refresh_token=refresh_token)
    api.clear_tokens()
    page.session.remove("user")
    page.session.remove("sf_access_token")
    page.session.remove("sf_refresh_token")
