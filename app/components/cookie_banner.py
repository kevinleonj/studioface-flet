"""StudioFace Cookie Banner — Dark premium GDPR-compliant banner."""

import flet as ft

from app.i18n import t
from app.theme import StudioFaceTheme as T

_COOKIE_KEY = "studioface_cookie_consent"


def build_cookie_banner(page: ft.Page, lang: str = "en") -> ft.Control:
    """Build a dark cookie consent banner with gold Accept button."""
    consent = page.session.store.get(_COOKIE_KEY)
    if consent is not None:
        return ft.Container(visible=False)

    banner_ref = ft.Ref[ft.Container]()

    def accept_cookies(e):
        page.session.store.set(_COOKIE_KEY, "accepted")
        if banner_ref.current:
            banner_ref.current.visible = False
            page.update()

    def decline_cookies(e):
        page.session.store.set(_COOKIE_KEY, "declined")
        if banner_ref.current:
            banner_ref.current.visible = False
            page.update()

    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    # Text section
    text_section = ft.Column(
        controls=[
            ft.Text(
                t("cookies.title", lang),
                size=T.FONT_H4,
                weight=ft.FontWeight.BOLD,
                color=T.TEXT_WHITE,
            ),
            ft.Text(
                t("cookies.desc", lang),
                size=T.FONT_CAPTION,
                color=T.TEXT_SECONDARY,
            ),
        ],
        spacing=T.SPACE_XS,
        expand=True,
    )

    # Gold Accept button
    accept_button = ft.ElevatedButton(
        t("cookies.accept", lang),
        on_click=accept_cookies,
        bgcolor=T.BUTTON_PRIMARY_BG,
        color=T.BUTTON_TEXT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
        ),
    )

    # Outline Decline button
    decline_button = ft.OutlinedButton(
        t("cookies.decline", lang),
        on_click=decline_cookies,
        style=ft.ButtonStyle(
            color=T.TEXT_SECONDARY,
            side=ft.BorderSide(1, T.OUTLINE),
            shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
        ),
    )

    buttons = ft.Row(
        controls=[accept_button, decline_button],
        spacing=T.SPACE_SM,
    )

    if is_mobile:
        inner_layout = ft.Column(
            controls=[text_section, buttons],
            spacing=T.SPACE_MD,
        )
    else:
        inner_layout = ft.Row(
            controls=[text_section, buttons],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_LG,
        )

    return ft.Container(
        ref=banner_ref,
        content=ft.Container(
            content=inner_layout,
            padding=ft.padding.symmetric(
                horizontal=T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING,
                vertical=T.SPACE_MD,
            ),
            width=T.MAX_WIDTH,
        ),
        bgcolor=T.BG_SURFACE_HIGH,
        alignment=ft.Alignment.CENTER,
        border=ft.border.only(top=ft.BorderSide(1, T.BORDER)),
    )
