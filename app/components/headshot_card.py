"""StudioFace Headshot Card — Display generated headshots with states."""

import flet as ft

from app.i18n import t
from app.theme import StudioFaceTheme as T


def build_headshot_card(
    image_url: str | None,
    variant_label: str,
    on_download,
    loading: bool = False,
    error: bool = False,
    lang: str = "en",
) -> ft.Control:
    """Build a headshot display card with loading, error, and loaded states."""
    card_width = 240
    image_height = 280

    # Determine content based on state
    if loading:
        # Loading state: grey background with spinner
        image_area = ft.Container(
            content=ft.Column(
                controls=[
                    ft.ProgressRing(
                        width=40,
                        height=40,
                        stroke_width=3,
                        color=T.PRIMARY,
                    ),
                    ft.Text(
                        t("common.loading", lang),
                        size=T.FONT_CAPTION,
                        color=T.TEXT_SECONDARY,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=T.SPACE_MD,
            ),
            width=card_width,
            height=image_height,
            bgcolor=T.SURFACE_VARIANT,
            border_radius=T.RADIUS_MD,
            alignment=ft.alignment.center,
        )
    elif error:
        # Error state: grey background with error icon
        image_area = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.ERROR_OUTLINE,
                        size=40,
                        color=T.ERROR,
                    ),
                    ft.Text(
                        t("error.generation_failed", lang),
                        size=T.FONT_CAPTION,
                        color=T.TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=T.SPACE_SM,
            ),
            width=card_width,
            height=image_height,
            bgcolor=T.SURFACE_VARIANT,
            border_radius=T.RADIUS_MD,
            alignment=ft.alignment.center,
        )
    else:
        # Loaded state: display the image
        image_area = ft.Container(
            content=ft.Image(
                src=image_url or "",
                fit=ft.ImageFit.COVER,
                width=card_width,
                height=image_height,
                border_radius=T.RADIUS_MD,
            ),
            width=card_width,
            height=image_height,
            border_radius=T.RADIUS_MD,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )

    # Variant label
    label = ft.Text(
        variant_label,
        size=T.FONT_CAPTION,
        color=T.TEXT_SECONDARY,
        text_align=ft.TextAlign.CENTER,
    )

    # Download button (only show when loaded and not error/loading)
    download_button = ft.OutlinedButton(
        text=t("gallery.download", lang),
        icon=ft.Icons.DOWNLOAD,
        on_click=on_download,
        visible=not loading and not error,
        style=ft.ButtonStyle(
            color=T.PRIMARY,
            side=ft.BorderSide(1, T.OUTLINE),
            shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
        ),
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                image_area,
                label,
                download_button,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_SM,
        ),
        padding=ft.padding.all(T.SPACE_SM),
        width=card_width + T.SPACE_MD * 2,
    )
