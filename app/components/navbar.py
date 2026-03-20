"""StudioFace Navigation Bar — Top bar with logo, nav links, auth controls."""

import flet as ft

from app.components.language_picker import build_language_picker
from app.i18n import t
from app.theme import StudioFaceTheme as T

# Route mapping for nav links
_NAV_LINKS = [
    ("nav.home", "/"),
    ("nav.create", "/create"),
    ("nav.gallery", "/gallery"),
]


def build_navbar(page: ft.Page) -> ft.Control:
    """Build top navigation bar with logo, links, language picker, and auth."""
    lang = page.session.store.get("lang") or "en"
    user = page.session.store.get("user")
    current_route = page.route or "/"

    def navigate(route):
        def handler(e):
            page.go(route)
        return handler

    def sign_out(e):
        page.session.store.remove("user")
        page.go("/")

    def sign_in(e):
        page.go("/login")

    # Logo
    logo = ft.TextButton(
        content=ft.Text(
            "StudioFace",
            size=T.FONT_H3,
            weight=ft.FontWeight.BOLD,
            color=T.PRIMARY,
        ),
        on_click=navigate("/"),
    )

    # Desktop nav links
    nav_links = []
    for key, route in _NAV_LINKS:
        is_active = current_route == route
        nav_links.append(
            ft.TextButton(
                content=ft.Text(
                    t(key, lang),
                    size=T.FONT_BODY,
                    weight=ft.FontWeight.W600 if is_active else ft.FontWeight.W400,
                    color=T.SECONDARY if is_active else T.TEXT_SECONDARY,
                ),
                on_click=navigate(route),
            )
        )

    # Language picker
    lang_picker = build_language_picker(page)

    # Auth section
    if user:
        user_email = user.get("email", "") if isinstance(user, dict) else str(user)
        auth_section = ft.Row(
            spacing=T.SPACE_SM,
            controls=[
                ft.Text(
                    user_email,
                    size=T.FONT_CAPTION,
                    color=T.TEXT_SECONDARY,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    width=120,
                ),
                ft.OutlinedButton(
                    text=t("nav.logout", lang),
                    on_click=sign_out,
                    style=ft.ButtonStyle(
                        color=T.TEXT_SECONDARY,
                        side=ft.BorderSide(1, T.OUTLINE),
                        shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                    ),
                ),
            ],
        )
    else:
        auth_section = ft.ElevatedButton(
            text=t("nav.login", lang),
            on_click=sign_in,
            bgcolor=T.PRIMARY,
            color=T.TEXT_ON_PRIMARY,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
            ),
        )

    # Mobile hamburger menu
    mobile_menu_items = []
    for key, route in _NAV_LINKS:
        mobile_menu_items.append(
            ft.PopupMenuItem(
                content=ft.Text(
                    t(key, lang),
                    color=T.SECONDARY if current_route == route else T.TEXT_PRIMARY,
                    weight=ft.FontWeight.W600 if current_route == route else ft.FontWeight.W400,
                ),
                on_click=navigate(route),
            ),
        )
    mobile_menu_items.append(ft.PopupMenuItem())  # divider
    if user:
        mobile_menu_items.append(
            ft.PopupMenuItem(
                content=ft.Text(t("nav.logout", lang), color=T.TEXT_PRIMARY),
                on_click=sign_out,
            ),
        )
    else:
        mobile_menu_items.append(
            ft.PopupMenuItem(
                content=ft.Text(t("nav.login", lang), color=T.PRIMARY),
                on_click=sign_in,
            ),
        )

    hamburger = ft.PopupMenuButton(
        icon=ft.Icons.MENU,
        icon_color=T.TEXT_PRIMARY,
        items=mobile_menu_items,
    )

    # Desktop layout: logo | nav links | lang picker + auth
    desktop_row = ft.Row(
        controls=[
            logo,
            ft.Row(controls=nav_links, spacing=T.SPACE_XS),
            ft.Row(
                controls=[lang_picker, auth_section],
                spacing=T.SPACE_MD,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

    # Mobile layout: logo | hamburger
    mobile_row = ft.Row(
        controls=[
            logo,
            ft.Row(
                controls=[lang_picker, hamburger],
                spacing=T.SPACE_XS,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

    # Determine which layout to show based on page width
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    content_row = mobile_row if is_mobile else desktop_row

    return ft.Container(
        content=ft.Container(
            content=content_row,
            padding=ft.padding.symmetric(
                horizontal=T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING,
                vertical=T.SPACE_SM,
            ),
            width=T.MAX_WIDTH,
        ),
        bgcolor=T.SURFACE,
        border=ft.border.only(bottom=ft.BorderSide(1, T.DIVIDER)),
        alignment=ft.alignment.center,
    )
