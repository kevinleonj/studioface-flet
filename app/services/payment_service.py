"""Payment service — Stripe checkout handling."""

from typing import Any

import flet as ft

from app.services.api_client import StudioFaceAPI


async def start_checkout(
    api: StudioFaceAPI, page: ft.Page, generation_id: str
) -> dict[str, Any]:
    """Create a Stripe checkout session and redirect."""
    result = await api.create_checkout(generation_id)
    if "error" in result:
        return result

    checkout_url = result.get("checkout_url") or result.get("url", "")
    if checkout_url:
        page.launch_url(checkout_url)
        return {"success": True, "url": checkout_url}

    return {"error": "No checkout URL returned", "code": "no_url", "status": 500}
