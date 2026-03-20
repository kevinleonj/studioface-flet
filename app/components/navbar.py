"""StudioFace Navigation Bar — Dark premium navbar matching production."""

import flet as ft

from app.components.language_picker import build_language_picker
from app.i18n import t
from app.theme import StudioFaceTheme as T


def build_navbar(page: ft.Page) -> ft.Control:
    """Build dark premium top navigation bar."""
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

    # Logo: orange square icon + "STUDIOFACE" bold white
    logo = ft.TextButton(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.SQUARE_ROUNDED,
                        color=T.PRIMARY_CONTAINER,
                        size=24,
                    ),
                    width=32,
                    height=32,
                    bgcolor=T.PRIMARY_CONTAINER,
                    border_radius=6,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Text(
                    "STUDIOFACE",
                    size=T.FONT_BODY,
                    weight=ft.FontWeight.BOLD,
                    color=T.TEXT_WHITE,
                ),
            ],
            spacing=T.SPACE_SM,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        on_click=navigate("/"),
    )

    # Right side: "My Headshots" link
    gallery_link = ft.TextButton(
        content=ft.Text(
            t("nav.gallery", lang),
            size=T.FONT_CAPTION,
            color=T.TEXT_SECONDARY,
        ),
        on_click=navigate("/gallery"),
    )

    # Language picker
    lang_picker = build_language_picker(page)

    # Avatar circle
    if user:
        user_email = user.get("email", "") if isinstance(user, dict) else str(user)
        avatar_letter = user_email[0].upper() if user_email else "U"
    else:
        avatar_letter = "U"

    avatar = ft.Container(
        content=ft.Text(
            avatar_letter,
            size=T.FONT_CAPTION,
            weight=ft.FontWeight.BOLD,
            color=T.ON_PRIMARY,
            text_align=ft.TextAlign.CENTER,
        ),
        width=36,
        height=36,
        bgcolor=T.PRIMARY_CONTAINER,
        border_radius=18,
        alignment=ft.Alignment.CENTER,
        on_click=sign_in if not user else sign_out,
    )

    # Mobile hamburger menu
    mobile_menu_items = [
        ft.PopupMenuItem(
            content=ft.Text(
                t("nav.home", lang),
                color=T.PRIMARY if current_route == "/" else T.TEXT_PRIMARY,
                weight=ft.FontWeight.W_600 if current_route == "/" else ft.FontWeight.W_400,
            ),
            on_click=navigate("/"),
        ),
        ft.PopupMenuItem(
            content=ft.Text(
                t("nav.create", lang),
                color=T.PRIMARY if current_route == "/create" else T.TEXT_PRIMARY,
                weight=ft.FontWeight.W_600 if current_route == "/create" else ft.FontWeight.W_400,
            ),
            on_click=navigate("/create"),
        ),
        ft.PopupMenuItem(
            content=ft.Text(
                t("nav.gallery", lang),
                color=T.PRIMARY if current_route.startswith("/gallery") else T.TEXT_PRIMARY,
                weight=ft.FontWeight.W_600 if current_route.startswith("/gallery") else ft.FontWeight.W_400,
            ),
            on_click=navigate("/gallery"),
        ),
        ft.PopupMenuItem(),  # divider
    ]
    if user:
        mobile_menu_items.append(
            ft.PopupMenuItem(
                content=ft.Text(t("nav.logout", lang), color=T.TEXT_SECONDARY),
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

    # Desktop layout
    desktop_row = ft.Row(
        controls=[
            logo,
            ft.Row(
                controls=[gallery_link, lang_picker, avatar],
                spacing=T.SPACE_MD,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

    # Mobile layout
    mobile_row = ft.Row(
        controls=[
            logo,
            ft.Row(
                controls=[lang_picker, hamburger],
                spacing=T.SPACE_XS,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

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
        bgcolor=T.BG_PRIMARY,
        height=T.NAV_HEIGHT,
        alignment=ft.Alignment.CENTER,
    )
