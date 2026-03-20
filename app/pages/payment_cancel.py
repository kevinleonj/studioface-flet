"""StudioFace Payment Cancel Page — shown when user cancels Stripe checkout."""

import flet as ft

from app.components.footer import build_footer
from app.components.navbar import build_navbar
from app.i18n import t
from app.theme import StudioFaceTheme as T


def build(page: ft.Page) -> list[ft.Control]:
    """Build the payment cancellation page. Returns list[ft.Control]."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    def go_create(e):
        page.go("/create")

    def go_home(e):
        page.go("/")

    cancel_icon = ft.Icon(
        ft.Icons.CANCEL_OUTLINED,
        size=80,
        color=T.TEXT_MUTED,
    )

    title = ft.Text(
        t("payment.cancel_title", lang),
        size=T.FONT_H2,
        weight=ft.FontWeight.BOLD,
        color=T.TEXT_WHITE,
        text_align=ft.TextAlign.CENTER,
    )

    desc = ft.Text(
        t("payment.cancel_desc", lang),
        size=T.FONT_BODY,
        color=T.TEXT_SECONDARY,
        text_align=ft.TextAlign.CENTER,
    )

    try_again_btn = ft.ElevatedButton(
        t("common.retry", lang),
        icon=ft.Icons.REFRESH,
        on_click=go_create,
        bgcolor=T.BUTTON_PRIMARY_BG,
        color=T.BUTTON_TEXT,
        height=48,
        width=250,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
            text_style=ft.TextStyle(
                size=T.FONT_BODY,
                weight=ft.FontWeight.W_600,
            ),
        ),
    )

    home_link = ft.TextButton(
        content=ft.Text(
            t("auth.back_home", lang),
            size=T.FONT_CAPTION,
            color=T.PRIMARY,
        ),
        on_click=go_home,
    )

    card_content = ft.Container(
        content=ft.Column(
            controls=[
                cancel_icon,
                title,
                desc,
                ft.Container(height=T.SPACE_MD),
                try_again_btn,
                home_link,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=T.SPACE_MD,
        ),
        padding=ft.padding.all(T.CARD_PADDING if not is_mobile else T.MOBILE_PADDING),
        width=500 if not is_mobile else None,
        bgcolor=T.BG_SURFACE,
        border_radius=T.RADIUS_LG,
        border=ft.border.all(1, T.BORDER),
    )

    centered_card = ft.Container(
        content=card_content,
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=ft.padding.symmetric(
            horizontal=T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING,
        ),
    )

    main_content = ft.Container(
        content=centered_card,
        expand=True,
        bgcolor=T.BG_PRIMARY,
    )

    return [
        build_navbar(page),
        main_content,
        build_footer(page),
    ]
