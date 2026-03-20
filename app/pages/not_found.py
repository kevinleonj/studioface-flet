"""StudioFace 404 Page — Dark premium not found page."""

import flet as ft

from app.components.footer import build_footer
from app.components.navbar import build_navbar
from app.i18n import t
from app.theme import StudioFaceTheme as T


def build(page: ft.Page) -> list[ft.Control]:
    """Build the 404 not found page. Returns list[ft.Control]."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    def go_home(e):
        page.go("/")

    # Large 404 text in TEXT_MUTED
    error_code = ft.Text(
        "404",
        size=T.FONT_HERO * 2.5 if not is_mobile else T.FONT_HERO * 1.8,
        weight=ft.FontWeight.W_900,
        color=T.TEXT_MUTED,
        text_align=ft.TextAlign.CENTER,
    )

    # Title
    title = ft.Text(
        t("error.not_found", lang),
        size=T.FONT_H2,
        weight=ft.FontWeight.BOLD,
        color=T.TEXT_WHITE,
        text_align=ft.TextAlign.CENTER,
    )

    # Subtitle
    subtitle = ft.Text(
        t("error.not_found_desc", lang),
        size=T.FONT_BODY,
        color=T.TEXT_SECONDARY,
        text_align=ft.TextAlign.CENTER,
    )

    # Gold "Go Home" button
    go_home_btn = ft.ElevatedButton(
        t("error.go_home", lang),
        on_click=go_home,
        bgcolor=T.BUTTON_PRIMARY_BG,
        color=T.BUTTON_TEXT,
        height=48,
        width=200,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
            text_style=ft.TextStyle(
                size=T.FONT_BODY,
                weight=ft.FontWeight.W_600,
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
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=ft.padding.symmetric(
            horizontal=T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING,
        ),
    )

    # Main content area
    main_content = ft.Container(
        content=centered_content,
        expand=True,
        bgcolor=T.BG_PRIMARY,
    )

    return [
        build_navbar(page),
        main_content,
        build_footer(page),
    ]
