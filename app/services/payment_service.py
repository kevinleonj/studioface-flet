"""Payment service — Stripe checkout handling."""

from typing import Any

import flet as ft

from app.services.api_client import StudioFaceAPI


async def start_checkout(
    api: StudioFaceAPI, page: ft.Page, generation_id: str, currency: str = "EUR"
) -> dict[str, Any]:
    """Create a Stripe checkout session and redirect.

    Args:
        api: API client instance.
        page: Flet page for launching the checkout URL.
        generation_id: The generation to pay for.
        currency: Payment currency (e.g. "EUR", "USD").
    """
    result = await api.create_checkout(generation_id, currency=currency)
    if "error" in result:
        return result

    checkout_url = result.get("checkout_url") or result.get("url", "")
    if checkout_url:
        page.launch_url(checkout_url)
        return {"success": True, "url": checkout_url}

    return {"error": "No checkout URL returned", "code": "no_url", "status": 500}
