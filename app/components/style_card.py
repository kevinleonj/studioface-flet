"""StudioFace Style Card — Dark premium selectable card with real photos."""

import flet as ft

from app.i18n import t
from app.theme import StudioFaceTheme as T

# Map theme STYLE_ICONS string names to ft.Icons enum values
_ICON_MAP = {
    "business_center": ft.Icons.BUSINESS_CENTER,
    "local_hospital": ft.Icons.LOCAL_HOSPITAL,
    "account_balance": ft.Icons.ACCOUNT_BALANCE,
    "rocket_launch": ft.Icons.ROCKET_LAUNCH,
    "emoji_people": ft.Icons.EMOJI_PEOPLE,
    "computer": ft.Icons.COMPUTER,
}


def build_style_card(
    style_key: str,
    lang: str,
    selected: bool,
    on_click,
) -> ft.Control:
    """Build a dark selectable style card with real photo if available."""
    style_color = T.STYLE_COLORS.get(style_key, T.PRIMARY)
    icon_name = T.STYLE_ICONS.get(style_key, "computer")
    icon_value = _ICON_MAP.get(icon_name, ft.Icons.COMPUTER)

    style_name = t(f"style.{style_key}", lang)
    style_desc = t(f"style.{style_key}.desc", lang)
    photo_url = T.STYLE_PHOTOS.get(style_key, "")

    # Border changes based on selection
    if selected:
        card_border = ft.border.all(3, T.PRIMARY_CONTAINER)
    else:
        card_border = ft.border.all(1, T.BORDER)

    # Image or colored top band
    if photo_url:
        top_band = ft.Container(
            content=ft.Image(
                src=photo_url,
                fit=ft.BoxFit.COVER,
                height=100,
            ),
            height=100,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            border_radius=ft.border_radius.only(
                top_left=T.RADIUS_MD,
                top_right=T.RADIUS_MD,
            ),
        )
    else:
        top_band = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(icon_value, size=32, color=T.TEXT_WHITE),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=style_color,
            height=80,
            border_radius=ft.border_radius.only(
                top_left=T.RADIUS_MD,
                top_right=T.RADIUS_MD,
            ),
            alignment=ft.Alignment.CENTER,
        )

    # Selection checkmark badge
    checkmark = ft.Container(
        content=ft.Icon(
            ft.Icons.CHECK_CIRCLE,
            size=24,
            color=T.PRIMARY_CONTAINER,
        ),
        visible=selected,
        alignment=ft.Alignment.TOP_RIGHT,
        padding=ft.padding.all(T.SPACE_XS),
    )

    # Text content below the band
    text_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    style_name,
                    size=T.FONT_H4,
                    weight=ft.FontWeight.BOLD,
                    color=T.TEXT_WHITE,
                ),
                ft.Text(
                    style_desc,
                    size=T.FONT_CAPTION,
                    color=T.TEXT_SECONDARY,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
            spacing=T.SPACE_XS,
        ),
        padding=ft.padding.all(T.SPACE_MD),
    )

    # Full card
    return ft.Container(
        content=ft.Stack(
            controls=[
                ft.Column(
                    controls=[top_band, text_content],
                    spacing=0,
                ),
                checkmark,
            ],
        ),
        border=card_border,
        border_radius=T.RADIUS_MD,
        bgcolor=T.BG_SURFACE,
        width=200,
        ink=True,
        on_click=on_click,
    )
