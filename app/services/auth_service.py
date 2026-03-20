"""Authentication service — login flows and token management."""

from typing import Any, Optional

import flet as ft

from app.services.api_client import StudioFaceAPI


async def login_with_magic_link(
    api: StudioFaceAPI, email: str
) -> dict[str, Any]:
    """Request a magic link email."""
    return await api.send_magic_link(email)


async def login_with_microsoft(api: StudioFaceAPI) -> dict[str, Any]:
    """Get the Microsoft OAuth URL."""
    return await api.get_microsoft_auth_url()


async def verify_and_store_token(
    api: StudioFaceAPI, page: ft.Page, token: str
) -> dict[str, Any]:
    """Verify a token and store it on success."""
    result = await api.verify_token(token)
    if "error" not in result:
        api.token = token
        page.session.store.set("sf_token", token)
        page.session.store.set("user", result)
    return result


async def restore_session(api: StudioFaceAPI, page: ft.Page) -> Optional[dict[str, Any]]:
    """Try to restore a session from stored token."""
    token = page.session.store.get("sf_token")
    if not token:
        return None
    api.token = token
    result = await api.get_current_user()
    if "error" in result:
        api.token = None
        page.session.store.remove("sf_token")
        return None
    page.session.store.set("user", result)
    return result


async def logout(api: StudioFaceAPI, page: ft.Page) -> None:
    """Clear auth state."""
    api.token = None
    page.session.store.remove("user")
    page.session.store.remove("sf_token")
