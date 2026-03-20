"""StudioFace Language Picker — Dark premium dropdown to switch EN/ES/DE."""

import flet as ft

from app.i18n import LANGUAGES
from app.theme import StudioFaceTheme as T


def build_language_picker(page: ft.Page) -> ft.Control:
    """Build a dark language selector dropdown with flag emojis."""
    current_lang = page.session.store.get("lang") or "en"

    def on_lang_change(e):
        new_lang = e.control.value
        page.session.store.set("lang", new_lang)
        current_route = page.route or "/"
        page.go(current_route)

    options = []
    for code, info in LANGUAGES.items():
        options.append(
            ft.dropdown.Option(
                key=code,
                text=f"{info['flag']} {info['name']}",
            )
        )

    return ft.Dropdown(
        value=current_lang,
        options=options,
        on_select=on_lang_change,
        width=160,
        height=42,
        text_size=T.FONT_CAPTION,
        content_padding=ft.padding.only(left=T.SPACE_SM, right=T.SPACE_XS),
        border_color=T.OUTLINE,
        focused_border_color=T.PRIMARY,
        border_radius=T.RADIUS_SM,
        bgcolor=T.BG_SURFACE,
        color=T.TEXT_PRIMARY,
    )
