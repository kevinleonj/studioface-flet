"""StudioFace Gallery Page — View and download generated headshots."""

import flet as ft

from app.components.navbar import build_navbar
from app.i18n import t
from app.services.api_client import StudioFaceAPI
from app.theme import StudioFaceTheme as T


def _build_footer(lang: str) -> ft.Control:
    """Minimal footer."""
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(t("footer.copyright", lang), size=T.FONT_SMALL, color=T.TEXT_SECONDARY),
                ft.Text(t("footer.gdpr", lang), size=T.FONT_SMALL, color=T.TEXT_SECONDARY),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=T.SPACE_LG,
        ),
        padding=ft.padding.symmetric(vertical=T.SPACE_LG, horizontal=T.CONTENT_PADDING),
        border=ft.border.only(top=ft.BorderSide(1, T.DIVIDER)),
    )


def _build_status_badge(status: str, lang: str) -> ft.Control:
    """Build a colored status chip based on generation status."""
    status_lower = status.lower()
    if status_lower in ("completed", "complete", "done"):
        bg = T.SUCCESS_CONTAINER
        fg = T.SUCCESS
        label_key = "gallery.status_completed"
        icon = ft.Icons.CHECK_CIRCLE
    elif status_lower in ("processing", "pending", "queued", "generating"):
        bg = T.WARNING_CONTAINER
        fg = T.WARNING
        label_key = "gallery.status_processing"
        icon = ft.Icons.HOURGLASS_TOP
    elif status_lower in ("partial",):
        bg = T.WARNING_CONTAINER
        fg = T.WARNING
        label_key = "gallery.status_partial"
        icon = ft.Icons.WARNING_AMBER
    else:
        bg = T.ERROR_CONTAINER
        fg = T.ERROR
        label_key = "gallery.status_failed"
        icon = ft.Icons.ERROR_OUTLINE

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icon, size=16, color=fg),
                ft.Text(
                    t(label_key, lang),
                    size=T.FONT_SMALL,
                    color=fg,
                    weight=ft.FontWeight.W600,
                ),
            ],
            spacing=T.SPACE_XS,
            tight=True,
        ),
        bgcolor=bg,
        border_radius=T.RADIUS_PILL,
        padding=ft.padding.symmetric(horizontal=T.SPACE_MD, vertical=T.SPACE_XS),
    )


def _build_empty_state(page: ft.Page, lang: str) -> ft.Control:
    """Empty state when user has no headshots."""
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=T.SPACE_HERO),
                ft.Icon(ft.Icons.PHOTO_LIBRARY_OUTLINED, size=80, color=T.TEXT_DISABLED),
                ft.Text(
                    t("gallery.empty", lang),
                    size=T.FONT_H3,
                    weight=ft.FontWeight.W600,
                    color=T.TEXT_PRIMARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=T.SPACE_MD),
                ft.ElevatedButton(
                    text=t("gallery.create_new", lang),
                    icon=ft.Icons.ADD_A_PHOTO,
                    bgcolor=T.SECONDARY,
                    color=T.TEXT_ON_SECONDARY,
                    on_click=lambda _: page.go("/create"),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                        padding=ft.padding.symmetric(horizontal=T.SPACE_XL, vertical=T.SPACE_MD),
                    ),
                ),
                ft.Container(height=T.SPACE_HERO),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_SM,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
        expand=True,
    )


def _build_error_state(lang: str, on_retry) -> ft.Control:
    """Error state with retry button."""
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=T.SPACE_HERO),
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color=T.ERROR),
                ft.Text(
                    t("error.generic", lang),
                    size=T.FONT_H4,
                    color=T.TEXT_PRIMARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=T.SPACE_MD),
                ft.ElevatedButton(
                    text=t("common.retry", lang),
                    icon=ft.Icons.REFRESH,
                    bgcolor=T.PRIMARY,
                    color=T.TEXT_ON_PRIMARY,
                    on_click=on_retry,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                        padding=ft.padding.symmetric(horizontal=T.SPACE_LG, vertical=T.SPACE_MD),
                    ),
                ),
                ft.Container(height=T.SPACE_HERO),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_SM,
        ),
        alignment=ft.alignment.center,
        expand=True,
    )


def _build_loading_state(lang: str) -> ft.Control:
    """Loading state with spinner."""
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=T.SPACE_HERO),
                ft.ProgressRing(
                    width=48,
                    height=48,
                    stroke_width=4,
                    color=T.PRIMARY,
                ),
                ft.Text(
                    t("common.loading", lang),
                    size=T.FONT_BODY,
                    color=T.TEXT_SECONDARY,
                ),
                ft.Container(height=T.SPACE_HERO),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_MD,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
        expand=True,
    )


def _build_image_card(
    image_data: dict,
    index: int,
    lang: str,
    page: ft.Page,
    is_mobile: bool,
) -> ft.Control:
    """Build a single headshot image card."""
    image_url = image_data.get("url") or image_data.get("image_url", "")
    variant_label = image_data.get("variant") or image_data.get("label") or f"#{index + 1}"

    async def download_image(e):
        if image_url:
            page.launch_url(image_url)

    card_width = None  # Let ResponsiveRow handle sizing

    # Image display with error handling
    image_control = ft.Image(
        src=image_url,
        fit=ft.ImageFit.COVER,
        width=None,
        height=280 if not is_mobile else 220,
        border_radius=ft.border_radius.only(
            top_left=T.RADIUS_MD,
            top_right=T.RADIUS_MD,
        ),
        error_content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.BROKEN_IMAGE, size=40, color=T.TEXT_DISABLED),
                    ft.Text(
                        t("error.generic", lang),
                        size=T.FONT_SMALL,
                        color=T.TEXT_DISABLED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=T.SPACE_SM,
            ),
            height=280 if not is_mobile else 220,
            bgcolor=T.SURFACE_VARIANT,
            alignment=ft.alignment.center,
            border_radius=ft.border_radius.only(
                top_left=T.RADIUS_MD,
                top_right=T.RADIUS_MD,
            ),
        ),
    )

    # Card footer with variant label and download button
    card_footer = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(
                    variant_label,
                    size=T.FONT_CAPTION,
                    color=T.TEXT_SECONDARY,
                    weight=ft.FontWeight.W500,
                ),
                ft.IconButton(
                    icon=ft.Icons.DOWNLOAD,
                    icon_color=T.PRIMARY,
                    icon_size=20,
                    tooltip=t("gallery.download", lang),
                    on_click=download_image,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=T.SPACE_MD, vertical=T.SPACE_SM),
    )

    return ft.Container(
        content=ft.Column(
            controls=[image_control, card_footer],
            spacing=0,
        ),
        border=ft.border.all(1, T.OUTLINE_VARIANT),
        border_radius=T.RADIUS_MD,
        bgcolor=T.SURFACE,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=4,
            color=ft.Colors.with_opacity(0.08, T.TEXT_PRIMARY),
            offset=ft.Offset(0, 2),
        ),
        width=card_width,
    )


def _build_past_generation_row(gen: dict, lang: str, page: ft.Page) -> ft.Control:
    """Build a row for a past generation in the history list."""
    gen_id = gen.get("id") or gen.get("generation_id", "")
    status = gen.get("status", "unknown")
    style = gen.get("style", "")
    created_at = gen.get("created_at") or gen.get("created", "")

    # Format date — just show the raw string if it's already formatted
    date_str = str(created_at)[:10] if created_at else ""

    style_display = t(f"style.{style}", lang) if style else ""

    async def view_generation(e):
        page.session.store.set("current_generation_id", gen_id)
        page.go("/gallery")

    status_lower = status.lower()
    if status_lower in ("completed", "complete", "done"):
        status_color = T.SUCCESS
        status_icon = ft.Icons.CHECK_CIRCLE
    elif status_lower in ("processing", "pending", "queued", "generating"):
        status_color = T.WARNING
        status_icon = ft.Icons.HOURGLASS_TOP
    else:
        status_color = T.ERROR
        status_icon = ft.Icons.ERROR_OUTLINE

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(status_icon, size=18, color=status_color),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    t("gallery.style_label", lang, style=style_display),
                                    size=T.FONT_BODY,
                                    color=T.TEXT_PRIMARY,
                                    weight=ft.FontWeight.W500,
                                ),
                                ft.Text(
                                    t("gallery.created_on", lang, date=date_str),
                                    size=T.FONT_SMALL,
                                    color=T.TEXT_SECONDARY,
                                ),
                            ],
                            spacing=2,
                        ),
                    ],
                    spacing=T.SPACE_MD,
                ),
                ft.TextButton(
                    content=ft.Text(
                        t("gallery.download", lang),
                        size=T.FONT_CAPTION,
                        color=T.PRIMARY,
                    ),
                    on_click=view_generation,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=T.SPACE_MD, vertical=T.SPACE_MD),
        border=ft.border.only(bottom=ft.BorderSide(1, T.DIVIDER)),
    )


async def build(page: ft.Page) -> ft.View:
    """Build the Gallery page."""
    lang = page.session.store.get("lang") or "en"
    api: StudioFaceAPI = page.session.store.get("api")
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX
    h_pad = T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING

    # Start with loading state
    body_content = _build_loading_state(lang)

    view = ft.View(
        route="/gallery",
        controls=[
            build_navbar(page),
            ft.Container(
                content=ft.Container(
                    content=body_content,
                    width=T.MAX_WIDTH,
                    padding=ft.padding.symmetric(horizontal=h_pad, vertical=T.SPACE_LG),
                ),
                expand=True,
                bgcolor=T.BACKGROUND,
                alignment=ft.alignment.top_center,
            ),
            _build_footer(lang),
        ],
        bgcolor=T.BACKGROUND,
        padding=0,
        spacing=0,
    )

    # --- Async data loading ---
    async def load_gallery():
        try:
            # Fetch all generations
            generations_result = await api.list_generations()

            if "error" in generations_result:
                await _show_error()
                return

            # The API may return a list directly or wrapped in a key
            if isinstance(generations_result, list):
                generations = generations_result
            else:
                generations = (
                    generations_result.get("generations")
                    or generations_result.get("data")
                    or generations_result.get("items")
                    or []
                )

            if not generations:
                await _show_empty()
                return

            # Find the current/most recent generation
            current_gen_id = page.session.store.get("current_generation_id")
            current_gen = None

            if current_gen_id:
                current_gen = next(
                    (g for g in generations
                     if (g.get("id") or g.get("generation_id")) == current_gen_id),
                    None,
                )

            if not current_gen and generations:
                current_gen = generations[0]

            # Load images for the current generation
            gen_id = current_gen.get("id") or current_gen.get("generation_id", "")
            status = current_gen.get("status", "unknown")

            images: list[dict] = []
            if status.lower() in ("completed", "complete", "done"):
                images_result = await api.get_generation_images(gen_id)
                if "error" not in images_result:
                    if isinstance(images_result, list):
                        images = images_result
                    else:
                        images = (
                            images_result.get("images")
                            or images_result.get("data")
                            or images_result.get("items")
                            or []
                        )

            await _show_gallery(current_gen, images, generations)

        except Exception:
            await _show_error()

    async def _show_empty():
        """Show empty state."""
        view.controls = [
            build_navbar(page),
            ft.Container(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                t("gallery.title", lang),
                                size=T.FONT_H1,
                                weight=ft.FontWeight.BOLD,
                                color=T.TEXT_PRIMARY,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            _build_empty_state(page, lang),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=T.SPACE_MD,
                    ),
                    width=T.MAX_WIDTH,
                    padding=ft.padding.symmetric(horizontal=h_pad, vertical=T.SPACE_LG),
                ),
                expand=True,
                bgcolor=T.BACKGROUND,
                alignment=ft.alignment.top_center,
            ),
            _build_footer(lang),
        ]
        page.update()

    async def _show_error():
        """Show error state."""
        async def retry(e):
            view.controls = [
                build_navbar(page),
                ft.Container(
                    content=ft.Container(
                        content=_build_loading_state(lang),
                        width=T.MAX_WIDTH,
                        padding=ft.padding.symmetric(horizontal=h_pad, vertical=T.SPACE_LG),
                    ),
                    expand=True,
                    bgcolor=T.BACKGROUND,
                    alignment=ft.alignment.top_center,
                ),
                _build_footer(lang),
            ]
            page.update()
            await load_gallery()

        view.controls = [
            build_navbar(page),
            ft.Container(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                t("gallery.title", lang),
                                size=T.FONT_H1,
                                weight=ft.FontWeight.BOLD,
                                color=T.TEXT_PRIMARY,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            _build_error_state(lang, retry),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=T.SPACE_MD,
                    ),
                    width=T.MAX_WIDTH,
                    padding=ft.padding.symmetric(horizontal=h_pad, vertical=T.SPACE_LG),
                ),
                expand=True,
                bgcolor=T.BACKGROUND,
                alignment=ft.alignment.top_center,
            ),
            _build_footer(lang),
        ]
        page.update()

    async def _show_gallery(
        current_gen: dict,
        images: list[dict],
        all_generations: list[dict],
    ):
        """Show the full gallery with images and history."""
        status = current_gen.get("status", "unknown")
        gen_id = current_gen.get("id") or current_gen.get("generation_id", "")

        # Header row: title + download all button
        header_controls: list[ft.Control] = [
            ft.Text(
                t("gallery.title", lang),
                size=T.FONT_H1,
                weight=ft.FontWeight.BOLD,
                color=T.TEXT_PRIMARY,
            ),
        ]

        if images:
            async def download_all(e):
                for img in images:
                    url = img.get("url") or img.get("image_url", "")
                    if url:
                        page.launch_url(url)

            header_controls.append(
                ft.OutlinedButton(
                    text=t("gallery.download_all", lang),
                    icon=ft.Icons.DOWNLOAD,
                    on_click=download_all,
                    style=ft.ButtonStyle(
                        color=T.PRIMARY,
                        side=ft.BorderSide(1, T.PRIMARY),
                        shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                        padding=ft.padding.symmetric(horizontal=T.SPACE_LG, vertical=T.SPACE_SM),
                    ),
                ),
            )

        header_row = ft.Row(
            controls=header_controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            wrap=True,
        )

        # Status badge
        status_badge = _build_status_badge(status, lang)

        # Content body
        body_controls: list[ft.Control] = [header_row, status_badge]

        if images:
            # Image grid — 2x2 desktop, 1 column mobile
            image_cards = []
            for i, img in enumerate(images):
                card = _build_image_card(img, i, lang, page, is_mobile)
                image_cards.append(
                    ft.Container(
                        content=card,
                        col={"xs": 12, "sm": 6},
                    )
                )

            image_grid = ft.ResponsiveRow(
                controls=image_cards,
                spacing=T.SPACE_MD,
                run_spacing=T.SPACE_MD,
            )
            body_controls.append(image_grid)

        elif status.lower() in ("processing", "pending", "queued", "generating"):
            # Still processing — show progress
            body_controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(height=T.SPACE_XL),
                            ft.ProgressRing(
                                width=48,
                                height=48,
                                stroke_width=4,
                                color=T.SECONDARY,
                            ),
                            ft.Text(
                                t("gallery.status_processing", lang),
                                size=T.FONT_BODY,
                                color=T.TEXT_SECONDARY,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=T.SPACE_XL),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=T.SPACE_MD,
                    ),
                    alignment=ft.alignment.center,
                )
            )

        elif status.lower() in ("failed", "error"):
            # Failed generation
            body_controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(height=T.SPACE_XL),
                            ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=T.ERROR),
                            ft.Text(
                                t("gallery.status_failed", lang),
                                size=T.FONT_BODY,
                                color=T.ERROR,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.ElevatedButton(
                                text=t("gallery.create_new", lang),
                                icon=ft.Icons.ADD_A_PHOTO,
                                bgcolor=T.SECONDARY,
                                color=T.TEXT_ON_SECONDARY,
                                on_click=lambda _: page.go("/create"),
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                                    padding=ft.padding.symmetric(
                                        horizontal=T.SPACE_XL, vertical=T.SPACE_MD,
                                    ),
                                ),
                            ),
                            ft.Container(height=T.SPACE_XL),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=T.SPACE_MD,
                    ),
                    alignment=ft.alignment.center,
                )
            )

        # Past generations list
        other_gens = [
            g for g in all_generations
            if (g.get("id") or g.get("generation_id")) != gen_id
        ]

        if other_gens:
            body_controls.append(ft.Container(height=T.SPACE_LG))
            body_controls.append(ft.Divider(color=T.DIVIDER, thickness=1))
            body_controls.append(ft.Container(height=T.SPACE_SM))

            past_rows = [
                _build_past_generation_row(g, lang, page)
                for g in other_gens
            ]

            body_controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=past_rows,
                        spacing=0,
                    ),
                    border=ft.border.all(1, T.OUTLINE_VARIANT),
                    border_radius=T.RADIUS_MD,
                    bgcolor=T.SURFACE,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                )
            )

        # "Create New" button at bottom
        body_controls.append(
            ft.Container(
                content=ft.OutlinedButton(
                    text=t("gallery.create_new", lang),
                    icon=ft.Icons.ADD_A_PHOTO,
                    on_click=lambda _: page.go("/create"),
                    style=ft.ButtonStyle(
                        color=T.SECONDARY,
                        side=ft.BorderSide(1, T.SECONDARY),
                        shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                        padding=ft.padding.symmetric(horizontal=T.SPACE_LG, vertical=T.SPACE_MD),
                    ),
                ),
                alignment=ft.alignment.center,
                padding=ft.padding.only(top=T.SPACE_LG),
            )
        )

        view.controls = [
            build_navbar(page),
            ft.Container(
                content=ft.Container(
                    content=ft.Column(
                        controls=body_controls,
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                        spacing=T.SPACE_MD,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    width=T.MAX_WIDTH,
                    padding=ft.padding.symmetric(horizontal=h_pad, vertical=T.SPACE_LG),
                ),
                expand=True,
                bgcolor=T.BACKGROUND,
                alignment=ft.alignment.top_center,
            ),
            _build_footer(lang),
        ]
        page.update()

    # Kick off async loading after view is returned
    page.run_task(load_gallery)

    return view
