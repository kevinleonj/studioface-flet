"""StudioFace Login Page — Dark premium design with gold accent and real API calls."""

import re

import flet as ft

from app.components.cookie_banner import build_cookie_banner
from app.components.footer import build_footer
from app.components.navbar import build_navbar
from app.i18n import t
from app.theme import StudioFaceTheme as T

# Simple email validation pattern
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def build(page: ft.Page) -> list[ft.Control]:
    """Build the login page with dark card and gold button. Returns list[ft.Control]."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    # If already authenticated, redirect to /create
    user = page.session.store.get("user")
    if user:
        page.go("/create")
        return []

    # Refs for dynamic elements
    email_field_ref = ft.Ref[ft.TextField]()
    send_button_ref = ft.Ref[ft.ElevatedButton]()
    error_banner_ref = ft.Ref[ft.Container]()
    success_banner_ref = ft.Ref[ft.Container]()
    form_column_ref = ft.Ref[ft.Column]()
    error_text_ref = ft.Ref[ft.Text]()

    def _validate_email(email: str) -> bool:
        return bool(_EMAIL_RE.match(email.strip()))

    def on_send_magic_link(e):
        email_field = email_field_ref.current
        send_button = send_button_ref.current
        error_banner = error_banner_ref.current
        success_banner = success_banner_ref.current

        if not email_field or not send_button:
            return

        email = email_field.value.strip() if email_field.value else ""

        if not email:
            email_field.error_text = t("auth.email_placeholder", lang)
            page.update()
            return

        if not _validate_email(email):
            email_field.error_text = t("auth.email_placeholder", lang)
            page.update()
            return

        email_field.error_text = None

        # Disable button and show loading
        send_button.disabled = True
        send_button.content = ft.Row(
            controls=[
                ft.ProgressRing(width=16, height=16, stroke_width=2, color=T.BUTTON_TEXT),
                ft.Text(
                    t("common.loading", lang),
                    size=T.FONT_BODY,
                    weight=ft.FontWeight.W_600,
                    color=T.BUTTON_TEXT,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=T.SPACE_SM,
        )
        if error_banner:
            error_banner.visible = False
        page.update()

        async def do_send():
            api = page.session.store.get("api")
            if not api:
                send_button.disabled = False
                send_button.content = ft.Text(
                    t("auth.send_magic_link", lang),
                    size=T.FONT_BODY,
                    weight=ft.FontWeight.W_600,
                    color=T.BUTTON_TEXT,
                )
                if error_banner:
                    error_text = error_text_ref.current
                    if error_text:
                        error_text.value = t("error.generic", lang)
                    error_banner.visible = True
                page.update()
                return

            result = await api.send_magic_link(email, lang)

            # Restore button
            send_button.disabled = False
            send_button.content = ft.Text(
                t("auth.send_magic_link", lang),
                size=T.FONT_BODY,
                weight=ft.FontWeight.W_600,
                color=T.BUTTON_TEXT,
            )

            if "error" not in result:
                # Success — show check email message
                if success_banner:
                    success_banner.visible = True
                if form_column_ref.current:
                    form_column_ref.current.visible = False
                if error_banner:
                    error_banner.visible = False
            else:
                # Error — show error banner
                if error_banner:
                    error_text = error_text_ref.current
                    if error_text:
                        error_text.value = result.get("error", t("error.generic", lang))
                    error_banner.visible = True
            page.update()

        page.run_task(do_send)

    def on_microsoft_login(e):
        microsoft_button = microsoft_button_ref.current
        if not microsoft_button:
            return

        microsoft_button.disabled = True
        page.update()

        async def do_microsoft():
            api = page.session.store.get("api")
            if not api:
                microsoft_button.disabled = False
                page.update()
                return

            result = await api.get_microsoft_auth_url()
            microsoft_button.disabled = False

            if "error" not in result:
                auth_url = result.get("auth_url", "")
                if auth_url:
                    page.launch_url(auth_url)
            else:
                error_banner = error_banner_ref.current
                if error_banner:
                    error_text = error_text_ref.current
                    if error_text:
                        error_text.value = result.get("error", t("error.generic", lang))
                    error_banner.visible = True
            page.update()

        page.run_task(do_microsoft)

    def on_back_home(e):
        page.go("/")

    # Refs
    microsoft_button_ref = ft.Ref[ft.OutlinedButton]()

    # Error banner (hidden by default)
    error_banner = ft.Container(
        ref=error_banner_ref,
        content=ft.Text(
            "",
            ref=error_text_ref,
            size=T.FONT_CAPTION,
            color=T.ERROR,
        ),
        bgcolor=ft.Colors.with_opacity(0.15, T.ERROR),
        border_radius=T.RADIUS_SM,
        padding=ft.padding.symmetric(horizontal=T.SPACE_MD, vertical=T.SPACE_SM),
        visible=False,
    )

    # Success banner (hidden by default)
    success_banner = ft.Container(
        ref=success_banner_ref,
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.MARK_EMAIL_READ, color=T.SUCCESS, size=48),
                ft.Container(height=T.SPACE_MD),
                ft.Text(
                    t("auth.check_email", lang),
                    size=T.FONT_H4,
                    weight=ft.FontWeight.W_600,
                    color=T.SUCCESS,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        padding=ft.padding.all(T.SPACE_XL),
        visible=False,
    )

    # Email text field (dark themed)
    email_field = ft.TextField(
        ref=email_field_ref,
        label=t("auth.email_placeholder", lang),
        hint_text="name@example.com",
        keyboard_type=ft.KeyboardType.EMAIL,
        border_radius=T.RADIUS_SM,
        border_color=T.OUTLINE,
        focused_border_color=T.PRIMARY,
        text_size=T.FONT_BODY,
        color=T.TEXT_PRIMARY,
        label_style=ft.TextStyle(color=T.TEXT_SECONDARY),
        hint_style=ft.TextStyle(color=T.TEXT_MUTED),
        bgcolor=T.BG_SURFACE_HIGH,
        content_padding=ft.padding.symmetric(horizontal=T.SPACE_MD, vertical=T.SPACE_MD),
    )

    # Gold "Send Magic Link" button
    send_button = ft.ElevatedButton(
        ref=send_button_ref,
        content=ft.Text(
            t("auth.send_magic_link", lang),
            size=T.FONT_BODY,
            weight=ft.FontWeight.W_600,
            color=T.BUTTON_TEXT,
        ),
        bgcolor=T.BUTTON_PRIMARY_BG,
        color=T.BUTTON_TEXT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
        ),
        width=350,
        height=48,
        on_click=on_send_magic_link,
    )

    # Divider with "or" text
    divider_row = ft.Row(
        controls=[
            ft.Container(
                content=ft.Divider(color=T.DIVIDER),
                expand=True,
            ),
            ft.Text(
                t("auth.or", lang),
                size=T.FONT_CAPTION,
                color=T.TEXT_MUTED,
            ),
            ft.Container(
                content=ft.Divider(color=T.DIVIDER),
                expand=True,
            ),
        ],
        spacing=T.SPACE_MD,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Microsoft login button
    microsoft_button = ft.OutlinedButton(
        t("auth.microsoft_login", lang),
        ref=microsoft_button_ref,
        icon=ft.Icons.WINDOW,
        style=ft.ButtonStyle(
            color=T.TEXT_PRIMARY,
            side=ft.BorderSide(1, T.OUTLINE),
            shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
        ),
        width=350,
        height=48,
        on_click=on_microsoft_login,
    )

    # Back to home link
    back_link = ft.TextButton(
        content=ft.Text(
            t("auth.back_home", lang),
            size=T.FONT_CAPTION,
            color=T.PRIMARY,
        ),
        on_click=on_back_home,
    )

    # Form column
    form_column = ft.Column(
        ref=form_column_ref,
        controls=[
            email_field,
            ft.Container(height=T.SPACE_SM),
            send_button,
            ft.Container(height=T.SPACE_LG),
            divider_row,
            ft.Container(height=T.SPACE_LG),
            microsoft_button,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )

    # Login card (dark surface)
    login_card = ft.Container(
        content=ft.Column(
            controls=[
                # Logo
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.SQUARE_ROUNDED,
                                color=T.PRIMARY_CONTAINER,
                                size=20,
                            ),
                            width=28,
                            height=28,
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
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=T.SPACE_SM,
                ),
                ft.Container(height=T.SPACE_SM),
                ft.Text(
                    t("auth.title", lang),
                    size=T.FONT_H3,
                    weight=ft.FontWeight.W_600,
                    color=T.TEXT_WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=T.SPACE_LG),
                error_banner,
                success_banner,
                form_column,
                ft.Container(height=T.SPACE_LG),
                back_link,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        width=420,
        bgcolor=T.BG_SURFACE,
        border_radius=T.RADIUS_LG,
        padding=ft.padding.all(T.SPACE_XL),
        border=ft.border.all(1, T.BORDER),
    )

    # Centered content area
    content_area = ft.Container(
        content=login_card,
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=ft.padding.symmetric(
            horizontal=T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING,
            vertical=T.SPACE_HERO,
        ),
    )

    return [
        build_navbar(page),
        content_area,
        build_footer(page),
        build_cookie_banner(page, lang),
    ]
