"""StudioFace Footer — Product links, legal links, copyright bar."""

import flet as ft

from app.i18n import t
from app.theme import StudioFaceTheme as T


def build_footer(page: ft.Page) -> ft.Control:
    """Build footer with product links, legal links, and copyright bar."""
    lang = page.session.store.get("lang") or "en"

    def navigate(route):
        def handler(e):
            page.go(route)
        return handler

    # Product links column
    product_links = ft.Column(
        spacing=T.SPACE_SM,
        controls=[
            ft.Text(
                t("footer.product", lang),
                size=T.FONT_BODY,
                weight=ft.FontWeight.BOLD,
                color=T.TEXT_PRIMARY,
            ),
            ft.TextButton(
                content=ft.Text(
                    t("nav.home", lang),
                    size=T.FONT_CAPTION,
                    color=T.TEXT_SECONDARY,
                ),
                on_click=navigate("/"),
            ),
            ft.TextButton(
                content=ft.Text(
                    t("nav.create", lang),
                    size=T.FONT_CAPTION,
                    color=T.TEXT_SECONDARY,
                ),
                on_click=navigate("/create"),
            ),
            ft.TextButton(
                content=ft.Text(
                    t("nav.gallery", lang),
                    size=T.FONT_CAPTION,
                    color=T.TEXT_SECONDARY,
                ),
                on_click=navigate("/gallery"),
            ),
        ],
    )

    # Legal links column
    legal_links = ft.Column(
        spacing=T.SPACE_SM,
        controls=[
            ft.Text(
                t("footer.legal", lang),
                size=T.FONT_BODY,
                weight=ft.FontWeight.BOLD,
                color=T.TEXT_PRIMARY,
            ),
            ft.TextButton(
                content=ft.Text(
                    t("footer.privacy", lang),
                    size=T.FONT_CAPTION,
                    color=T.TEXT_SECONDARY,
                ),
                on_click=navigate("/privacy"),
            ),
            ft.TextButton(
                content=ft.Text(
                    t("footer.terms", lang),
                    size=T.FONT_CAPTION,
                    color=T.TEXT_SECONDARY,
                ),
                on_click=navigate("/terms"),
            ),
        ],
    )

    # Links row
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    if is_mobile:
        links_section = ft.Column(
            controls=[product_links, legal_links],
            spacing=T.SPACE_LG,
        )
    else:
        links_section = ft.Row(
            controls=[product_links, legal_links],
            spacing=T.SPACE_HERO,
            alignment=ft.MainAxisAlignment.START,
        )

    # Bottom copyright bar
    copyright_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(
                    t("footer.copyright", lang) + " \u00b7 " + t("footer.made_in", lang) + " \U0001f1ea\U0001f1f8",
                    size=T.FONT_SMALL,
                    color=T.TEXT_SECONDARY,
                ),
                ft.Text(
                    t("footer.gdpr", lang),
                    size=T.FONT_SMALL,
                    color=T.TEXT_SECONDARY,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.only(top=T.SPACE_MD),
        border=ft.border.only(top=ft.BorderSide(1, T.DIVIDER)),
    )

    # Full footer
    return ft.Container(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    links_section,
                    copyright_bar,
                ],
                spacing=T.SPACE_LG,
            ),
            padding=ft.padding.symmetric(
                horizontal=T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING,
                vertical=T.SPACE_XL,
            ),
            width=T.MAX_WIDTH,
        ),
        bgcolor=T.SURFACE_VARIANT,
        border=ft.border.only(top=ft.BorderSide(1, T.DIVIDER)),
        alignment=ft.alignment.center,
    )
