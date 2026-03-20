"""StudioFace Loading Spinner — Gold spinner on dark background."""

import flet as ft

from app.theme import StudioFaceTheme as T


def build_loading_spinner(message: str = "") -> ft.Control:
    """Build a centered loading spinner with an optional message below it."""
    controls = [
        ft.ProgressRing(
            width=48,
            height=48,
            stroke_width=3,
            color=T.PRIMARY_CONTAINER,
        ),
    ]

    if message:
        controls.append(
            ft.Text(
                message,
                size=T.FONT_BODY,
                color=T.TEXT_SECONDARY,
                text_align=ft.TextAlign.CENTER,
            )
        )

    return ft.Container(
        content=ft.Column(
            controls=controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=T.SPACE_MD,
        ),
        alignment=ft.Alignment.CENTER,
        expand=True,
        padding=ft.padding.all(T.SPACE_XXL),
        bgcolor=T.BG_PRIMARY,
    )
