"""StudioFace Upload Zone — Dashed-border file upload area with file chips."""

import flet as ft

from app.i18n import t
from app.theme import StudioFaceTheme as T


def build_upload_zone(
    page: ft.Page,
    file_picker: ft.FilePicker,
    uploaded_files: list,
    on_remove_file,
    lang: str = "en",
) -> ft.Control:
    """Build a file upload zone with dashed border, instructions, and file chips."""

    def pick_files(e):
        file_picker.pick_files(
            allow_multiple=True,
            allowed_extensions=["jpg", "jpeg", "png"],
            dialog_title=t("create.upload_button", lang),
        )

    # File chips showing uploaded file names
    file_chips = []
    for i, f in enumerate(uploaded_files):
        file_name = f.name if hasattr(f, "name") else str(f)
        file_chips.append(
            ft.Chip(
                label=ft.Text(
                    file_name,
                    size=T.FONT_SMALL,
                    color=T.TEXT_PRIMARY,
                ),
                delete_icon=ft.Icons.CLOSE,
                on_delete=lambda e, idx=i: on_remove_file(idx),
                bgcolor=T.PRIMARY_CONTAINER,
                delete_icon_color=T.TEXT_SECONDARY,
            )
        )

    # File count text
    file_count_text = ft.Text(
        t("create.uploaded_count", lang, count=len(uploaded_files)),
        size=T.FONT_CAPTION,
        color=T.PRIMARY,
        weight=ft.FontWeight.W500,
        visible=len(uploaded_files) > 0,
    )

    # Chips row (wrapping)
    chips_row = ft.Row(
        controls=file_chips,
        wrap=True,
        spacing=T.SPACE_SM,
        run_spacing=T.SPACE_SM,
        visible=len(uploaded_files) > 0,
    )

    # Upload zone content
    upload_content = ft.Column(
        controls=[
            ft.Icon(
                ft.Icons.CAMERA_ALT_OUTLINED,
                size=48,
                color=T.TEXT_DISABLED,
            ),
            ft.Text(
                t("create.upload_title", lang),
                size=T.FONT_H4,
                weight=ft.FontWeight.W600,
                color=T.TEXT_PRIMARY,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Text(
                t("create.upload_desc", lang),
                size=T.FONT_CAPTION,
                color=T.TEXT_SECONDARY,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(height=T.SPACE_SM),
            ft.ElevatedButton(
                text=t("create.upload_button", lang),
                icon=ft.Icons.ADD_PHOTO_ALTERNATE_OUTLINED,
                on_click=pick_files,
                bgcolor=T.PRIMARY,
                color=T.TEXT_ON_PRIMARY,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                ),
            ),
            file_count_text,
            chips_row,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=T.SPACE_SM,
    )

    # Dashed border container
    # Flet doesn't support dashed borders natively, so we use a dotted visual
    # approach with border + styling to approximate it
    return ft.Container(
        content=upload_content,
        padding=ft.padding.all(T.SPACE_XL),
        border=ft.border.all(2, T.OUTLINE),
        border_radius=T.RADIUS_MD,
        bgcolor=T.SURFACE_VARIANT,
        alignment=ft.alignment.center,
        ink=True,
        on_click=pick_files,
    )
