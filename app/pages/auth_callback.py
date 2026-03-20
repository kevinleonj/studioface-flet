"""StudioFace Auth Callback Page — handles magic link and Microsoft OAuth returns."""

from urllib.parse import parse_qs, urlparse

import flet as ft

from app.i18n import t
from app.theme import StudioFaceTheme as T


def build(page: ft.Page) -> list[ft.Control]:
    """Build the auth callback page. Returns list[ft.Control].

    Parses token/code/state from the URL, calls the appropriate API
    endpoint, stores tokens on success, and redirects.
    """
    lang = page.session.store.get("lang") or "en"

    # --- Parse query params from page.route ---
    route = page.route or ""
    params: dict[str, str] = {}
    if "?" in route:
        qs = route.split("?", 1)[1]
        parsed = parse_qs(qs)
        for key, values in parsed.items():
            if values:
                params[key] = values[0]

    # --- Status text ref for updating from async ---
    status_text = ft.Text(
        t("auth.verifying", lang),
        size=T.FONT_H4,
        weight=ft.FontWeight.W_600,
        color=T.TEXT_WHITE,
        text_align=ft.TextAlign.CENTER,
    )

    spinner = ft.ProgressRing(
        width=48,
        height=48,
        stroke_width=4,
        color=T.PRIMARY_CONTAINER,
    )

    error_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color=T.ERROR),
                ft.Text(
                    t("auth.verify_error", lang),
                    size=T.FONT_H4,
                    weight=ft.FontWeight.W_600,
                    color=T.ERROR,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=T.SPACE_MD),
                ft.ElevatedButton(
                    t("nav.login", lang),
                    icon=ft.Icons.LOGIN,
                    bgcolor=T.BUTTON_PRIMARY_BG,
                    color=T.BUTTON_TEXT,
                    on_click=lambda _: page.go("/login"),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                        padding=ft.padding.symmetric(
                            horizontal=T.SPACE_XL, vertical=T.SPACE_MD
                        ),
                    ),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_MD,
        ),
        visible=False,
    )

    loading_container = ft.Container(
        content=ft.Column(
            controls=[
                spinner,
                status_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_LG,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        visible=True,
    )

    def _store_tokens_and_redirect(result: dict) -> None:
        """Store auth tokens in session, configure API client, and navigate."""
        api = page.session.store.get("api")
        access_token = result.get("access_token", result.get("token", ""))
        refresh_token = result.get("refresh_token", "")

        if access_token and api:
            api.set_tokens(access_token, refresh_token)

        user_data = result.get("user") or {
            "id": result.get("id", ""),
            "email": result.get("email", ""),
            "name": result.get("name", ""),
        }
        page.session.store.set("user", user_data)
        page.session.store.set("access_token", access_token)
        page.session.store.set("refresh_token", refresh_token)

        page.go("/create")

    def _show_error(message: str) -> None:
        """Display error state with message."""
        loading_container.visible = False
        error_text = error_container.content.controls[1]
        error_text.value = message
        error_container.visible = True
        page.update()

    # --- Kick off verification immediately ---
    def _start_verification():
        token = params.get("token", "")
        code = params.get("code", "")
        state = params.get("state", "")

        if token:
            # Magic link flow
            async def verify_magic_link():
                api = page.session.store.get("api")
                if not api:
                    _show_error(t("error.generic", lang))
                    return
                result = await api.verify_token(token)
                if "error" in result:
                    _show_error(result.get("error", t("auth.verify_error", lang)))
                else:
                    _store_tokens_and_redirect(result)

            page.run_task(verify_magic_link)

        elif code:
            # Microsoft OAuth flow
            async def verify_microsoft():
                api = page.session.store.get("api")
                if not api:
                    _show_error(t("error.generic", lang))
                    return
                result = await api.microsoft_callback(code, state)
                if "error" in result:
                    _show_error(result.get("error", t("auth.verify_error", lang)))
                else:
                    _store_tokens_and_redirect(result)

            page.run_task(verify_microsoft)

        else:
            # No token or code — invalid callback
            _show_error(t("auth.verify_error", lang))

    _start_verification()

    # --- Layout ---
    card = ft.Container(
        content=ft.Column(
            controls=[
                loading_container,
                error_container,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_MD,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        width=420,
        bgcolor=T.BG_SURFACE,
        border_radius=T.RADIUS_LG,
        padding=ft.padding.all(T.SPACE_XXL),
        border=ft.border.all(1, T.BORDER),
    )

    content_area = ft.Container(
        content=card,
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=ft.padding.symmetric(
            horizontal=T.CONTENT_PADDING,
            vertical=T.SPACE_HERO,
        ),
    )

    return [content_area]
