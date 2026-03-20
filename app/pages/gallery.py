"""StudioFace Gallery Page — Dark premium design with real API calls."""

import flet as ft

from app.components.navbar import build_navbar
from app.i18n import t
from app.theme import StudioFaceTheme as T


def _build_gallery_footer(lang: str) -> ft.Control:
    """Minimal dark footer."""
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(t("footer.copyright", lang), size=T.FONT_SMALL, color=T.TEXT_MUTED),
                ft.Text(t("footer.gdpr", lang), size=T.FONT_SMALL, color=T.TEXT_MUTED),
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
        bg = ft.Colors.with_opacity(0.15, T.SUCCESS)
        fg = T.SUCCESS
        label_key = "gallery.status_completed"
        icon = ft.Icons.CHECK_CIRCLE
    elif status_lower in ("processing", "pending", "queued", "generating"):
        bg = ft.Colors.with_opacity(0.15, T.PRIMARY_CONTAINER)
        fg = T.PRIMARY_CONTAINER
        label_key = "gallery.status_processing"
        icon = ft.Icons.HOURGLASS_TOP
    elif status_lower in ("partial",):
        bg = ft.Colors.with_opacity(0.15, T.PRIMARY_CONTAINER)
        fg = T.PRIMARY_CONTAINER
        label_key = "gallery.status_partial"
        icon = ft.Icons.WARNING_AMBER
    else:
        bg = ft.Colors.with_opacity(0.15, T.ERROR)
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
                    weight=ft.FontWeight.W_600,
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
                ft.Icon(ft.Icons.PHOTO_LIBRARY_OUTLINED, size=80, color=T.TEXT_MUTED),
                ft.Text(
                    t("gallery.empty", lang),
                    size=T.FONT_H3,
                    weight=ft.FontWeight.W_600,
                    color=T.TEXT_WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=T.SPACE_MD),
                ft.ElevatedButton(
                    t("gallery.create_new", lang),
                    icon=ft.Icons.ADD_A_PHOTO,
                    bgcolor=T.BUTTON_PRIMARY_BG,
                    color=T.BUTTON_TEXT,
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
        alignment=ft.Alignment.CENTER,
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
                    color=T.TEXT_WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=T.SPACE_MD),
                ft.ElevatedButton(
                    t("common.retry", lang),
                    icon=ft.Icons.REFRESH,
                    bgcolor=T.BUTTON_PRIMARY_BG,
                    color=T.BUTTON_TEXT,
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
        alignment=ft.Alignment.CENTER,
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
                    color=T.PRIMARY_CONTAINER,
                ),
                ft.Text(
                    t("gallery.loading", lang),
                    size=T.FONT_BODY,
                    color=T.TEXT_SECONDARY,
                ),
                ft.Container(height=T.SPACE_HERO),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_MD,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        alignment=ft.Alignment.CENTER,
        expand=True,
    )


def _build_image_card(
    image_data: dict,
    index: int,
    lang: str,
    page: ft.Page,
    is_mobile: bool,
) -> ft.Control:
    """Build a single headshot image card (dark themed)."""
    image_url = image_data.get("url") or image_data.get("image_url", "")
    variant_label = image_data.get("variant") or image_data.get("label") or f"#{index + 1}"

    def download_image(e):
        if image_url:
            page.launch_url(image_url)

    image_control = ft.Image(
        src=image_url,
        fit=ft.BoxFit.COVER,
        width=None,
        height=280 if not is_mobile else 220,
        border_radius=ft.border_radius.only(
            top_left=T.RADIUS_MD,
            top_right=T.RADIUS_MD,
        ),
        error_content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.BROKEN_IMAGE, size=40, color=T.TEXT_MUTED),
                    ft.Text(
                        t("error.generic", lang),
                        size=T.FONT_SMALL,
                        color=T.TEXT_MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=T.SPACE_SM,
            ),
            height=280 if not is_mobile else 220,
            bgcolor=T.BG_SURFACE_HIGH,
            alignment=ft.Alignment.CENTER,
            border_radius=ft.border_radius.only(
                top_left=T.RADIUS_MD,
                top_right=T.RADIUS_MD,
            ),
        ),
    )

    card_footer = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(
                    variant_label,
                    size=T.FONT_CAPTION,
                    color=T.TEXT_SECONDARY,
                    weight=ft.FontWeight.W_500,
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
        border=ft.border.all(1, T.BORDER),
        border_radius=T.RADIUS_MD,
        bgcolor=T.BG_SURFACE,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )


def _build_generation_card(
    gen: dict,
    lang: str,
    page: ft.Page,
    is_mobile: bool,
) -> ft.Control:
    """Build a card for a single generation with its images."""
    status = gen.get("status", "unknown")
    style = gen.get("style", "")
    created_at = gen.get("created_at", gen.get("created", ""))
    results = gen.get("results", gen.get("images", []))

    # Format date
    date_str = ""
    if created_at:
        if isinstance(created_at, str) and len(created_at) >= 10:
            date_str = created_at[:10]
        else:
            date_str = str(created_at)

    # Header with status, style, and date
    header_controls: list[ft.Control] = [
        _build_status_badge(status, lang),
    ]
    if style:
        style_label = t(f"style.{style.lower()}", lang)
        header_controls.append(
            ft.Text(
                t("gallery.style_label", lang, style=style_label),
                size=T.FONT_CAPTION,
                color=T.TEXT_SECONDARY,
            ),
        )
    if date_str:
        header_controls.append(
            ft.Text(
                t("gallery.created_on", lang, date=date_str),
                size=T.FONT_CAPTION,
                color=T.TEXT_MUTED,
            ),
        )

    header = ft.Container(
        content=ft.Row(
            controls=header_controls,
            alignment=ft.MainAxisAlignment.START,
            spacing=T.SPACE_MD,
            wrap=True,
            run_spacing=T.SPACE_SM,
        ),
        padding=ft.padding.all(T.SPACE_MD),
    )

    card_controls: list[ft.Control] = [header]

    # Image grid for completed generations
    status_lower = status.lower()
    if status_lower in ("completed", "complete", "done") and results:
        image_cards = []
        for i, img in enumerate(results):
            if isinstance(img, str):
                img = {"url": img}
            image_cards.append(
                ft.Container(
                    content=_build_image_card(img, i, lang, page, is_mobile),
                    col={"xs": 12, "sm": 6},
                )
            )

        card_controls.append(
            ft.Container(
                content=ft.ResponsiveRow(
                    controls=image_cards,
                    spacing=T.SPACE_MD,
                    run_spacing=T.SPACE_MD,
                ),
                padding=ft.padding.symmetric(horizontal=T.SPACE_MD),
            )
        )
    elif status_lower in ("processing", "pending", "queued", "generating"):
        card_controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.ProgressRing(
                            width=32, height=32, stroke_width=3,
                            color=T.PRIMARY_CONTAINER,
                        ),
                        ft.Text(
                            t("gallery.status_processing", lang),
                            size=T.FONT_CAPTION,
                            color=T.TEXT_SECONDARY,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=T.SPACE_SM,
                ),
                padding=ft.padding.all(T.SPACE_LG),
                alignment=ft.Alignment.CENTER,
            )
        )

    return ft.Container(
        content=ft.Column(
            controls=card_controls,
            spacing=0,
        ),
        border=ft.border.all(1, T.BORDER),
        border_radius=T.RADIUS_LG,
        bgcolor=T.BG_SURFACE,
        margin=ft.margin.only(bottom=T.SPACE_LG),
    )


def build(page: ft.Page) -> list[ft.Control]:
    """Build the Gallery page with real API data. Returns list[ft.Control]."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX
    h_pad = T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING

    # Check auth
    user = page.session.store.get("user")
    if not user:
        page.go("/login")
        return []

    # State for dynamic content
    state = {
        "loaded": False,
        "error": False,
        "generations": [],
    }

    # Content column that gets updated
    body_content = ft.Column(
        controls=[
            ft.Text(
                t("gallery.title", lang),
                size=T.FONT_H1,
                weight=ft.FontWeight.BOLD,
                color=T.TEXT_WHITE,
                text_align=ft.TextAlign.CENTER,
            ),
            _build_loading_state(lang),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=T.SPACE_MD,
    )

    def _rebuild_content():
        """Rebuild gallery content based on state."""
        body_content.controls.clear()

        # Title + Create New button row
        title_row = ft.Row(
            controls=[
                ft.Text(
                    t("gallery.title", lang),
                    size=T.FONT_H1,
                    weight=ft.FontWeight.BOLD,
                    color=T.TEXT_WHITE,
                ),
                ft.ElevatedButton(
                    t("gallery.create_new", lang),
                    icon=ft.Icons.ADD_A_PHOTO,
                    bgcolor=T.BUTTON_PRIMARY_BG,
                    color=T.BUTTON_TEXT,
                    on_click=lambda _: page.go("/create"),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                        padding=ft.padding.symmetric(
                            horizontal=T.SPACE_LG, vertical=T.SPACE_SM
                        ),
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            wrap=True,
            run_spacing=T.SPACE_SM,
        )
        body_content.controls.append(title_row)

        if state["error"]:
            body_content.controls.append(
                _build_error_state(lang, on_retry=lambda _: _load_data())
            )
        elif not state["generations"]:
            body_content.controls.append(_build_empty_state(page, lang))
        else:
            for gen in state["generations"]:
                body_content.controls.append(
                    _build_generation_card(gen, lang, page, is_mobile)
                )

        page.update()

    def _load_data():
        """Kick off async data loading."""
        async def do_load():
            api = page.session.store.get("api")
            if not api:
                state["error"] = True
                state["loaded"] = True
                _rebuild_content()
                return

            result = await api.list_generations()

            if "error" in result:
                state["error"] = True
                state["loaded"] = True
                _rebuild_content()
                return

            # API returns either {"items": [...]} or {"generations": [...]} or a list
            generations = (
                result.get("items")
                or result.get("generations")
                or result.get("results")
                or (result if isinstance(result, list) else [])
            )
            state["generations"] = generations if isinstance(generations, list) else []
            state["loaded"] = True
            state["error"] = False
            _rebuild_content()

        page.run_task(do_load)

    # Start loading immediately
    _load_data()

    body = ft.Container(
        content=ft.Container(
            content=body_content,
            width=T.MAX_WIDTH,
            padding=ft.padding.symmetric(horizontal=h_pad, vertical=T.SPACE_LG),
        ),
        expand=True,
        bgcolor=T.BG_PRIMARY,
        alignment=ft.Alignment.TOP_CENTER,
    )

    return [
        build_navbar(page),
        body,
        _build_gallery_footer(lang),
    ]
