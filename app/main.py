"""StudioFace — Flet 0.82 app with page.controls routing."""

import os
import sys
import traceback

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import flet as ft

from app.services.api_client import StudioFaceAPI
from app.theme import StudioFaceTheme as T


def main(page: ft.Page):
    """Main entry point — sync, uses page.controls routing."""
    page.title = "StudioFace"
    page.padding = 0
    page.spacing = 0
    page.bgcolor = T.BG_PRIMARY
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO

    # Initialize API client
    api_url = os.environ.get(
        "STUDIOFACE_API_URL", "https://api.studioface.app/api/v1"
    )
    api = StudioFaceAPI(api_url)
    page.session.store.set("api", api)

    if not page.session.store.get("lang"):
        page.session.store.set("lang", "en")

    def navigate(route: str):
        """Clear page and load the correct page controls."""
        try:
            print(f"[NAV] route={route}", flush=True)
            page.controls.clear()
            page.scroll = ft.ScrollMode.AUTO

            # Strip query params for route matching
            route_path = route.split("?")[0] if "?" in route else route

            if route_path == "/" or route_path == "":
                from app.pages.landing import build
                page.controls.extend(build(page))
            elif route_path == "/login":
                from app.pages.login import build
                page.controls.extend(build(page))
            elif route_path.startswith("/auth/callback"):
                from app.pages.auth_callback import build
                page.controls.extend(build(page))
            elif route_path == "/create":
                from app.pages.create import build
                page.controls.extend(build(page))
            elif route_path.startswith("/gallery"):
                from app.pages.gallery import build
                page.controls.extend(build(page))
            elif route_path == "/payment/success":
                from app.pages.payment_success import build
                page.controls.extend(build(page))
            elif route_path == "/payment/cancel":
                from app.pages.payment_cancel import build
                page.controls.extend(build(page))
            else:
                from app.pages.not_found import build
                page.controls.extend(build(page))

            page.update()
            print(f"[NAV] rendered {route} OK", flush=True)
        except Exception:
            traceback.print_exc()

    def on_route_change(e):
        print(f"[ROUTE_CHANGE] route={page.route}", flush=True)
        navigate(page.route)

    page.on_route_change = on_route_change
    navigate("/")


ft.app(target=main)
