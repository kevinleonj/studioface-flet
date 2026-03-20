"""StudioFace Progress Tracker — Dark premium step indicator."""

import flet as ft

from app.theme import StudioFaceTheme as T


def build_progress_tracker(current_step: int, steps: list[str]) -> ft.Control:
    """Build a horizontal step indicator with gold active and muted future states.

    Args:
        current_step: 0-indexed current step number.
        steps: List of step label strings.
    """
    controls = []

    for i, label in enumerate(steps):
        is_completed = i < current_step
        is_current = i == current_step
        is_future = i > current_step

        # Circle content
        if is_completed:
            circle_content = ft.Icon(
                ft.Icons.CHECK,
                size=18,
                color=T.TEXT_WHITE,
            )
            circle_bgcolor = T.SUCCESS
            circle_border = None
        elif is_current:
            circle_content = ft.Text(
                str(i + 1),
                size=T.FONT_CAPTION,
                weight=ft.FontWeight.BOLD,
                color=T.ON_PRIMARY,
                text_align=ft.TextAlign.CENTER,
            )
            circle_bgcolor = T.PRIMARY_CONTAINER
            circle_border = None
        else:
            circle_content = ft.Text(
                str(i + 1),
                size=T.FONT_CAPTION,
                weight=ft.FontWeight.W_500,
                color=T.TEXT_MUTED,
                text_align=ft.TextAlign.CENTER,
            )
            circle_bgcolor = T.BG_SURFACE_HIGH
            circle_border = ft.border.all(2, T.OUTLINE_VARIANT)

        # Circle
        circle = ft.Container(
            content=circle_content,
            width=36,
            height=36,
            border_radius=18,
            bgcolor=circle_bgcolor,
            border=circle_border,
            alignment=ft.Alignment.CENTER,
        )

        # Label below circle
        label_color = T.TEXT_WHITE if is_current else (T.SUCCESS if is_completed else T.TEXT_MUTED)
        step_label = ft.Text(
            label,
            size=T.FONT_SMALL,
            color=label_color,
            weight=ft.FontWeight.W_500 if is_current else ft.FontWeight.W_400,
            text_align=ft.TextAlign.CENTER,
            width=80,
        )

        # Step column
        step_column = ft.Column(
            controls=[circle, step_label],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_XS,
        )

        controls.append(step_column)

        # Connecting line between steps
        if i < len(steps) - 1:
            line_color = T.SUCCESS if is_completed else T.BG_SURFACE_HIGH
            connecting_line = ft.Container(
                width=40,
                height=2,
                bgcolor=line_color,
                margin=ft.margin.only(bottom=T.SPACE_LG),
            )
            controls.append(connecting_line)

    return ft.Container(
        content=ft.Row(
            controls=controls,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=T.SPACE_SM,
        ),
        padding=ft.padding.symmetric(vertical=T.SPACE_MD),
    )
