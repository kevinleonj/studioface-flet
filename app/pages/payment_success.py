"""StudioFace Payment Success Page — Dark premium confirmation."""

import flet as ft

from app.components.footer import build_footer
from app.components.navbar import build_navbar
from app.i18n import t
from app.theme import StudioFaceTheme as T


def build(page: ft.Page) -> list[ft.Control]:
    """Build the payment success confirmation page. Returns list[ft.Control]."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    def go_gallery(e):
        page.go("/gallery")

    # Gold checkmark icon
    success_icon = ft.Icon(
        ft.Icons.CHECK_CIRCLE,
        size=80,
        color=T.PRIMARY_CONTAINER,
    )

    # Title
    title = ft.Text(
        t("payment.success_title", lang),
        size=T.FONT_H1,
        weight=ft.FontWeight.BOLD,
        color=T.TEXT_WHITE,
        text_align=ft.TextAlign.CENTER,
    )

    # Subtitle
    subtitle = ft.Text(
        t("payment.success_desc", lang),
        size=T.FONT_BODY,
        color=T.TEXT_SECONDARY,
        text_align=ft.TextAlign.CENTER,
    )

    # Gold CTA button
    view_gallery_btn = ft.ElevatedButton(
        t("payment.view_gallery", lang),
        on_click=go_gallery,
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

    # Email note
    email_note = ft.Text(
        t("payment.email_note", lang),
        size=T.FONT_CAPTION,
        color=T.TEXT_MUTED,
        text_align=ft.TextAlign.CENTER,
    )

    # Dark card
    card_content = ft.Container(
        content=ft.Column(
            controls=[
                success_icon,
                title,
                subtitle,
                ft.Container(height=T.SPACE_MD),
                view_gallery_btn,
                email_note,
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

    # Centered card wrapper
    centered_card = ft.Container(
        content=card_content,
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=ft.padding.symmetric(
            horizontal=T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING,
        ),
    )

    # Main content area
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
