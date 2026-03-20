"""StudioFace Upload Zone — Dark premium dashed-border file upload area.

Flet 0.82: FilePicker.pick_files() is async. We use page.run_task() to call
it from synchronous click handlers and invoke a callback with the results.
"""

from typing import Callable, Optional

import flet as ft

from app.i18n import t
from app.theme import StudioFaceTheme as T


def build_upload_zone(
    page: ft.Page,
    file_picker: ft.FilePicker,
    uploaded_files: list,
    on_remove_file: Callable[[int], None],
    lang: str = "en",
    on_files_picked: Optional[Callable[[list], None]] = None,
) -> ft.Control:
    """Build a dark file upload zone with dashed border."""

    def pick_files_click(e):
        """Trigger async file picker from a sync click handler via page.run_task."""
        async def do_pick():
            result = await file_picker.pick_files(
                allow_multiple=True,
                allowed_extensions=["jpg", "jpeg", "png"],
                dialog_title=t("create.upload_button", lang),
                file_type=ft.FilePickerFileType.CUSTOM,
            )
            if result and on_files_picked:
                on_files_picked(result)

        page.run_task(do_pick)

    # File chips showing uploaded file names
    file_chips = []
    for i, f in enumerate(uploaded_files):
        file_name = f.get("name") if isinstance(f, dict) else (f.name if hasattr(f, "name") else str(f))
        file_chips.append(
            ft.Chip(
                label=ft.Text(
                    file_name,
                    size=T.FONT_SMALL,
                    color=T.TEXT_PRIMARY,
                ),
                delete_icon=ft.Icons.CLOSE,
                on_delete=lambda e, idx=i: on_remove_file(idx),
                bgcolor=T.BG_SURFACE_HIGH,
                delete_icon_color=T.TEXT_SECONDARY,
            )
        )

    file_count_text = ft.Text(
        t("create.uploaded_count", lang, count=len(uploaded_files)),
        size=T.FONT_CAPTION,
        color=T.PRIMARY,
        weight=ft.FontWeight.W_500,
        visible=len(uploaded_files) > 0,
    )

    chips_row = ft.Row(
        controls=file_chips,
        wrap=True,
        spacing=T.SPACE_SM,
        run_spacing=T.SPACE_SM,
        visible=len(uploaded_files) > 0,
    )

    upload_content = ft.Column(
        controls=[
            ft.Icon(
                ft.Icons.CAMERA_ALT_OUTLINED,
                size=48,
                color=T.TEXT_MUTED,
            ),
            ft.Text(
                t("create.upload_title", lang),
                size=T.FONT_H4,
                weight=ft.FontWeight.W_600,
                color=T.TEXT_WHITE,
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
                t("create.upload_button", lang),
                icon=ft.Icons.ADD_PHOTO_ALTERNATE_OUTLINED,
                on_click=pick_files_click,
                bgcolor=T.BUTTON_PRIMARY_BG,
                color=T.BUTTON_TEXT,
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

    # Dashed border on dark BG_SURFACE
    return ft.Container(
        content=upload_content,
        padding=ft.padding.all(T.SPACE_XL),
        border=ft.border.all(2, T.OUTLINE),
        border_radius=T.RADIUS_MD,
        bgcolor=T.BG_SURFACE,
        alignment=ft.Alignment.CENTER,
        ink=True,
        on_click=pick_files_click,
    )
