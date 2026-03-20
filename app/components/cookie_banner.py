"""StudioFace Cookie Banner — GDPR-compliant cookie consent banner."""

import flet as ft

from app.i18n import t
from app.theme import StudioFaceTheme as T

_COOKIE_KEY = "studioface_cookie_consent"


def build_cookie_banner(page: ft.Page, lang: str = "en") -> ft.Control:
    """Build a GDPR cookie consent banner with dark background.

    Uses page.session to persist preference within the session.
    Returns an empty Container if consent has already been given or declined.
    """
    # Check session preference
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
                color=T.TEXT_ON_PRIMARY,
            ),
            ft.Text(
                t("cookies.desc", lang),
                size=T.FONT_CAPTION,
                color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE),
            ),
        ],
        spacing=T.SPACE_XS,
        expand=True,
    )

    # Accept button (SECONDARY colored)
    accept_button = ft.ElevatedButton(
        text=t("cookies.accept", lang),
        on_click=accept_cookies,
        bgcolor=T.SECONDARY,
        color=T.TEXT_ON_SECONDARY,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
        ),
    )

    # Decline button (outlined white)
    decline_button = ft.OutlinedButton(
        text=t("cookies.decline", lang),
        on_click=decline_cookies,
        style=ft.ButtonStyle(
            color=T.TEXT_ON_PRIMARY,
            side=ft.BorderSide(1, ft.Colors.with_opacity(0.5, ft.Colors.WHITE)),
            shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
        ),
    )

    buttons = ft.Row(
        controls=[accept_button, decline_button],
        spacing=T.SPACE_SM,
    )

    # Layout: mobile stacks vertically, desktop side-by-side
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
        bgcolor=T.PRIMARY_DARK,
        alignment=ft.alignment.center,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
            offset=ft.Offset(0, -2),
        ),
    )
