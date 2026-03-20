"""StudioFace — Professional AI Headshots. Main application entry point."""

import os
import sys

# Ensure the project root is in sys.path for module resolution
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import flet as ft
from dotenv import load_dotenv

from app.i18n import t
from app.services.api_client import StudioFaceAPI
from app.theme import StudioFaceTheme as T

load_dotenv()


async def main(page: ft.Page):
    """Initialize and run the StudioFace application."""
    lang = "en"

    page.title = t("hero.title", lang) + " | StudioFace"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme_seed=T.PRIMARY,
    )
    page.padding = 0
    page.bgcolor = T.BACKGROUND

    # Initialize API client
    api_url = os.getenv(
        "STUDIOFACE_API_URL", "https://api.studioface.app/api/v1"
    )
    api = StudioFaceAPI(api_url)
    page.session.store.set("api", api)
    page.session.store.set("lang", lang)

    # Try to restore session from stored token
    try:
        token = page.session.store.get("sf_token")
        if token:
            api.token = token
            user = await api.get_current_user()
            if "error" not in user:
                page.session.store.set("user", user)
            else:
                api.token = None
                page.session.store.remove("sf_token")
    except Exception:
        pass

    # Lazy imports to avoid circular dependencies and keep startup fast
    from app.pages import (  # noqa: E402
        not_found,
        payment_success,
    )

    async def route_change(e):
        """Handle route changes and render the correct page."""
        page.views.clear()
        route = page.route

        if route == "/" or route == "":
            # Landing page — lazy import
            from app.pages import landing

            view = await landing.build(page)
        elif route == "/login":
            from app.pages import login

            view = await login.build(page)
        elif route == "/create":
            from app.pages import create

            view = await create.build(page)
        elif route.startswith("/gallery"):
            from app.pages import gallery

            view = await gallery.build(page)
        elif route == "/payment/success":
            view = await payment_success.build(page)
        else:
            view = await not_found.build(page)

        page.views.append(view)
        page.update()

    async def view_pop(e):
        """Handle back navigation."""
        page.views.pop()
        if page.views:
            top_view = page.views[-1]
            page.go(top_view.route)
        page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.go("/")


if __name__ == "__main__":
    ft.run(main)
