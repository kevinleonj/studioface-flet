"""StudioFace Payment Success Page — Confirmation after successful payment."""

import flet as ft

from app.components.footer import build_footer
from app.components.navbar import build_navbar
from app.i18n import t
from app.theme import StudioFaceTheme as T


async def build(page: ft.Page) -> ft.View:
    """Build the payment success confirmation page."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    def go_gallery(e):
        page.go("/gallery")

    # Success icon
    success_icon = ft.Icon(
        name=ft.Icons.CHECK_CIRCLE,
        size=80,
        color=T.SUCCESS,
    )

    # Title
    title = ft.Text(
        t("payment.success_title", lang),
        size=T.FONT_H1,
        weight=ft.FontWeight.BOLD,
        color=T.TEXT_PRIMARY,
        text_align=ft.TextAlign.CENTER,
    )

    # Subtitle
    subtitle = ft.Text(
        t("payment.success_desc", lang),
        size=T.FONT_BODY,
        color=T.TEXT_SECONDARY,
        text_align=ft.TextAlign.CENTER,
    )

    # CTA button
    view_gallery_btn = ft.ElevatedButton(
        text=t("payment.view_gallery", lang),
        on_click=go_gallery,
        bgcolor=T.PRIMARY,
        color=T.TEXT_ON_PRIMARY,
        height=48,
        width=250,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
            text_style=ft.TextStyle(
                size=T.FONT_BODY,
                weight=ft.FontWeight.W600,
            ),
        ),
    )

    # Email note
    email_note = ft.Text(
        t("payment.email_note", lang),
        size=T.FONT_CAPTION,
        color=T.TEXT_DISABLED,
        text_align=ft.TextAlign.CENTER,
    )

    # Card content
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
        bgcolor=T.SURFACE,
        border_radius=T.RADIUS_MD,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )

    # Centered card wrapper
    centered_card = ft.Container(
        content=card_content,
        alignment=ft.alignment.center,
        expand=True,
        padding=ft.padding.symmetric(
            horizontal=T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING,
        ),
    )

    # Main content area
    main_content = ft.Container(
        content=centered_card,
        expand=True,
        bgcolor=T.BACKGROUND,
    )

    return ft.View(
        route="/payment/success",
        controls=[
            build_navbar(page),
            main_content,
            build_footer(page),
        ],
        padding=0,
        bgcolor=T.BACKGROUND,
        spacing=0,
    )
