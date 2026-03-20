"""StudioFace Login Page — Magic link and Microsoft sign-in."""

import re

import flet as ft

from app.components.cookie_banner import build_cookie_banner
from app.components.footer import build_footer
from app.components.navbar import build_navbar
from app.i18n import t
from app.theme import StudioFaceTheme as T

# Simple email validation pattern
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


async def build(page: ft.Page) -> ft.View:
    """Build the login page view with magic link and Microsoft auth."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    # Refs for dynamic elements
    email_field_ref = ft.Ref[ft.TextField]()
    send_button_ref = ft.Ref[ft.ElevatedButton]()
    microsoft_button_ref = ft.Ref[ft.OutlinedButton]()
    error_banner_ref = ft.Ref[ft.Container]()
    success_banner_ref = ft.Ref[ft.Container]()
    form_column_ref = ft.Ref[ft.Column]()

    def _validate_email(email: str) -> bool:
        return bool(_EMAIL_RE.match(email.strip()))

    async def on_send_magic_link(e: ft.ControlEvent) -> None:
        email_field = email_field_ref.current
        send_button = send_button_ref.current
        error_banner = error_banner_ref.current
        success_banner = success_banner_ref.current

        if not email_field or not send_button:
            return

        email = email_field.value.strip() if email_field.value else ""

        # Validate email
        if not email:
            email_field.error_text = t("auth.email_placeholder", lang)
            page.update()
            return

        if not _validate_email(email):
            email_field.error_text = t("auth.email_placeholder", lang)
            page.update()
            return

        email_field.error_text = None

        # Show loading state
        send_button.disabled = True
        send_button.text = t("common.loading", lang)
        page.update()

        try:
            api = page.session.store.get("api")
            if api is None:
                # Try to get from AppState
                state = page.session.store.get("state")
                if state:
                    api = state.api

            if api is None:
                if error_banner:
                    error_banner.content.value = t("error.generic", lang)
                    error_banner.visible = True
                send_button.disabled = False
                send_button.text = t("auth.send_magic_link", lang)
                page.update()
                return

            result = await api.send_magic_link(email)

            if "error" in result:
                if error_banner:
                    error_banner.content.value = result.get("error", t("error.generic", lang))
                    error_banner.visible = True
                if success_banner:
                    success_banner.visible = False
                send_button.disabled = False
                send_button.text = t("auth.send_magic_link", lang)
            else:
                # Success: show success message, hide form
                if success_banner:
                    success_banner.visible = True
                if error_banner:
                    error_banner.visible = False
                if form_column_ref.current:
                    form_column_ref.current.visible = False

            page.update()

        except Exception:
            if error_banner:
                error_banner.content.value = t("error.network", lang)
                error_banner.visible = True
            send_button.disabled = False
            send_button.text = t("auth.send_magic_link", lang)
            page.update()

    async def on_microsoft_login(e: ft.ControlEvent) -> None:
        microsoft_button = microsoft_button_ref.current
        error_banner = error_banner_ref.current

        if microsoft_button:
            microsoft_button.disabled = True
            page.update()

        try:
            api = page.session.store.get("api")
            if api is None:
                state = page.session.store.get("state")
                if state:
                    api = state.api

            if api is None:
                if error_banner:
                    error_banner.content.value = t("error.generic", lang)
                    error_banner.visible = True
                if microsoft_button:
                    microsoft_button.disabled = False
                page.update()
                return

            result = await api.get_microsoft_auth_url()

            if "error" in result:
                if error_banner:
                    error_banner.content.value = result.get("error", t("error.generic", lang))
                    error_banner.visible = True
                if microsoft_button:
                    microsoft_button.disabled = False
            else:
                auth_url = result.get("url", result.get("auth_url", ""))
                if auth_url:
                    page.launch_url(auth_url)
                if microsoft_button:
                    microsoft_button.disabled = False

            page.update()

        except Exception:
            if error_banner:
                error_banner.content.value = t("error.network", lang)
                error_banner.visible = True
            if microsoft_button:
                microsoft_button.disabled = False
            page.update()

    def on_back_home(e: ft.ControlEvent) -> None:
        page.go("/")

    # -- Build UI controls --

    # Error banner (hidden by default)
    error_banner = ft.Container(
        ref=error_banner_ref,
        content=ft.Text(
            "",
            size=T.FONT_CAPTION,
            color=T.ERROR,
        ),
        bgcolor=T.ERROR_CONTAINER,
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
                    weight=ft.FontWeight.W600,
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

    # Email text field
    email_field = ft.TextField(
        ref=email_field_ref,
        label=t("auth.email_placeholder", lang),
        hint_text="name@example.com",
        keyboard_type=ft.KeyboardType.EMAIL,
        border_radius=T.RADIUS_SM,
        border_color=T.OUTLINE_VARIANT,
        focused_border_color=T.PRIMARY,
        text_size=T.FONT_BODY,
        content_padding=ft.padding.symmetric(horizontal=T.SPACE_MD, vertical=T.SPACE_MD),
    )

    # Send magic link button
    send_button = ft.ElevatedButton(
        ref=send_button_ref,
        text=t("auth.send_magic_link", lang),
        bgcolor=T.PRIMARY,
        color=T.TEXT_ON_PRIMARY,
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
                color=T.TEXT_SECONDARY,
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
        ref=microsoft_button_ref,
        text=t("auth.microsoft_login", lang),
        icon=ft.Icons.WINDOW,
        style=ft.ButtonStyle(
            color=T.TEXT_PRIMARY,
            side=ft.BorderSide(1, T.OUTLINE_VARIANT),
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

    # Form column (hidden on success)
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

    # Login card
    login_card = ft.Container(
        content=ft.Column(
            controls=[
                # Logo text
                ft.Text(
                    "StudioFace",
                    size=T.FONT_H2,
                    weight=ft.FontWeight.BOLD,
                    color=T.PRIMARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=T.SPACE_SM),
                # Sign in title
                ft.Text(
                    t("auth.title", lang),
                    size=T.FONT_H3,
                    weight=ft.FontWeight.W600,
                    color=T.TEXT_PRIMARY,
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
        bgcolor=T.SURFACE,
        border_radius=T.RADIUS_LG,
        padding=ft.padding.all(T.SPACE_XL),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
            offset=ft.Offset(0, 4),
        ),
        border=ft.border.all(1, T.DIVIDER),
    )

    # Centered content area
    content_area = ft.Container(
        content=login_card,
        alignment=ft.alignment.center,
        expand=True,
        padding=ft.padding.symmetric(
            horizontal=T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING,
            vertical=T.SPACE_HERO,
        ),
    )

    return ft.View(
        route="/login",
        controls=[
            build_navbar(page),
            content_area,
            build_footer(page),
            build_cookie_banner(page, lang),
        ],
        scroll=ft.ScrollMode.AUTO,
        padding=0,
        bgcolor=T.BACKGROUND,
    )
