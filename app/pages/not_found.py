"""StudioFace 404 Page — Shown when a route does not exist."""

import flet as ft

from app.components.footer import build_footer
from app.components.navbar import build_navbar
from app.i18n import t
from app.theme import StudioFaceTheme as T


async def build(page: ft.Page) -> ft.View:
    """Build the 404 not found page."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    def go_home(e):
        page.go("/")

    # Large 404 text
    error_code = ft.Text(
        "404",
        size=T.FONT_HERO * 2.5 if not is_mobile else T.FONT_HERO * 1.8,
        weight=ft.FontWeight.W900,
        color=T.TEXT_DISABLED,
        text_align=ft.TextAlign.CENTER,
    )

    # Title
    title = ft.Text(
        t("error.not_found", lang),
        size=T.FONT_H2,
        weight=ft.FontWeight.BOLD,
        color=T.TEXT_PRIMARY,
        text_align=ft.TextAlign.CENTER,
    )

    # Subtitle
    subtitle = ft.Text(
        t("error.not_found_desc", lang),
        size=T.FONT_BODY,
        color=T.TEXT_SECONDARY,
        text_align=ft.TextAlign.CENTER,
    )

    # Go home button
    go_home_btn = ft.ElevatedButton(
        text=t("error.go_home", lang),
        on_click=go_home,
        bgcolor=T.PRIMARY,
        color=T.TEXT_ON_PRIMARY,
        height=48,
        width=200,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
            text_style=ft.TextStyle(
                size=T.FONT_BODY,
                weight=ft.FontWeight.W600,
            ),
        ),
    )

    # Centered content
    centered_content = ft.Container(
        content=ft.Column(
            controls=[
                error_code,
                title,
                subtitle,
                ft.Container(height=T.SPACE_MD),
                go_home_btn,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=T.SPACE_SM,
        ),
        alignment=ft.alignment.center,
        expand=True,
        padding=ft.padding.symmetric(
            horizontal=T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING,
        ),
    )

    # Main content area
    main_content = ft.Container(
        content=centered_content,
        expand=True,
        bgcolor=T.BACKGROUND,
    )

    return ft.View(
        route="/404",
        controls=[
            build_navbar(page),
            main_content,
            build_footer(page),
        ],
        padding=0,
        bgcolor=T.BACKGROUND,
        spacing=0,
    )
