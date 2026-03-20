"""StudioFace Create Page — 3-step wizard: Upload, Style, Presentation + Generate."""

import flet as ft

from app.components.navbar import build_navbar
from app.i18n import t
from app.services.api_client import StudioFaceAPI
from app.services.generation_service import create_generation
from app.services.payment_service import start_checkout
from app.services.upload_service import (
    create_session_and_upload,
    validate_file,
    validate_file_count,
)
from app.theme import StudioFaceTheme as T

# Style keys matching theme and i18n
_STYLES = ["corporate", "medical", "banking", "startup", "casual", "tech"]


def _build_progress_tracker(current_step: int, lang: str) -> ft.Control:
    """Build the 3-step progress indicator."""
    steps = [
        (1, "create.step_upload", ft.Icons.CLOUD_UPLOAD),
        (2, "create.step_style", ft.Icons.PALETTE),
        (3, "create.step_presentation", ft.Icons.CHECKROOM),
    ]
    items: list[ft.Control] = []
    for i, (num, key, icon) in enumerate(steps):
        is_active = num == current_step
        is_done = num < current_step

        if is_done:
            circle_bg = T.SUCCESS
            circle_content = ft.Icon(ft.Icons.CHECK, color=T.TEXT_ON_PRIMARY, size=18)
        elif is_active:
            circle_bg = T.PRIMARY
            circle_content = ft.Text(
                str(num), color=T.TEXT_ON_PRIMARY, size=T.FONT_CAPTION,
                weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,
            )
        else:
            circle_bg = T.OUTLINE_VARIANT
            circle_content = ft.Text(
                str(num), color=T.TEXT_SECONDARY, size=T.FONT_CAPTION,
                text_align=ft.TextAlign.CENTER,
            )

        circle = ft.Container(
            content=circle_content,
            width=36,
            height=36,
            border_radius=18,
            bgcolor=circle_bg,
            alignment=ft.alignment.center,
        )

        label = ft.Text(
            t(key, lang),
            size=T.FONT_SMALL,
            color=T.PRIMARY if is_active else (T.SUCCESS if is_done else T.TEXT_DISABLED),
            weight=ft.FontWeight.W600 if is_active else ft.FontWeight.W400,
            text_align=ft.TextAlign.CENTER,
        )

        step_col = ft.Column(
            controls=[circle, label],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_XS,
            width=80,
        )

        items.append(step_col)

        # Connector line between steps
        if i < len(steps) - 1:
            line_color = T.SUCCESS if num < current_step else T.OUTLINE_VARIANT
            items.append(
                ft.Container(
                    bgcolor=line_color,
                    height=2,
                    width=40,
                    margin=ft.margin.only(bottom=20),
                )
            )

    return ft.Container(
        content=ft.Row(
            controls=items,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(vertical=T.SPACE_LG),
    )


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


async def build(page: ft.Page) -> ft.View:
    """Build the Create page with a 3-step wizard."""
    lang = page.session.store.get("lang") or "en"
    api: StudioFaceAPI = page.session.store.get("api")
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX
    h_pad = T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING

    # --- Mutable wizard state ---
    current_step = 1
    selected_files: list[dict] = []  # [{name, size, bytes}]
    selected_style: str | None = None
    selected_presentation: str | None = None
    validation_error: str | None = None
    is_generating = False

    # --- Refs for dynamic content ---
    content_container = ft.Ref[ft.Container]()
    main_column = ft.Ref[ft.Column]()

    # --- File picker setup ---
    file_picker = ft.FilePicker()

    async def on_files_picked(e: ft.FilePickerResultEvent):
        nonlocal selected_files, validation_error
        if not e.files:
            return

        validation_error = None
        for f in e.files:
            # Check max count
            if len(selected_files) >= 5:
                validation_error = t("create.max_photos", lang)
                break

            # Validate format
            err = validate_file(f.name, f.size)
            if err:
                validation_error = t(err, lang)
                continue

            # Read file bytes
            try:
                with open(f.path, "rb") as fh:
                    file_bytes = fh.read()
            except Exception:
                validation_error = t("error.upload_failed", lang)
                continue

            # Avoid duplicates
            if any(sf["name"] == f.name for sf in selected_files):
                continue

            selected_files.append({
                "name": f.name,
                "size": f.size,
                "bytes": file_bytes,
            })

        await _rebuild_step()

    file_picker.on_result = on_files_picked

    # Add file picker to overlay
    page.overlay.append(file_picker)

    # --- Navigation handlers ---
    async def go_next(e):
        nonlocal current_step, validation_error
        if current_step == 1:
            count_err = validate_file_count(len(selected_files))
            if count_err:
                validation_error = t(count_err, lang)
                await _rebuild_step()
                return
            validation_error = None
            current_step = 2
        elif current_step == 2:
            if not selected_style:
                return
            current_step = 3
        await _rebuild_step()

    async def go_back(e):
        nonlocal current_step
        if current_step > 1:
            current_step -= 1
            await _rebuild_step()

    # --- File removal ---
    def make_remove_handler(filename: str):
        async def handler(e):
            nonlocal selected_files, validation_error
            selected_files = [f for f in selected_files if f["name"] != filename]
            validation_error = None
            await _rebuild_step()
        return handler

    # --- Style selection ---
    def make_style_handler(style: str):
        async def handler(e):
            nonlocal selected_style
            selected_style = style
            await _rebuild_step()
        return handler

    # --- Presentation selection ---
    def make_presentation_handler(pres: str):
        async def handler(e):
            nonlocal selected_presentation
            selected_presentation = pres
            await _rebuild_step()
        return handler

    # --- Generate handler ---
    async def on_generate(e):
        nonlocal is_generating, validation_error
        if not selected_style or not selected_presentation or len(selected_files) < 2:
            return

        is_generating = True
        await _rebuild_step()

        try:
            # 1. Upload files
            files_to_upload = [(f["name"], f["bytes"]) for f in selected_files]
            upload_result = await create_session_and_upload(api, files_to_upload)
            if "error" in upload_result:
                is_generating = False
                validation_error = upload_result["error"]
                await _rebuild_step()
                return

            session_id = upload_result["session_id"]

            # 2. Create generation
            gen_result = await create_generation(
                api, session_id, selected_style, selected_presentation,
            )
            if "error" in gen_result:
                is_generating = False
                validation_error = gen_result["error"]
                await _rebuild_step()
                return

            generation_id = gen_result.get("generation_id") or gen_result.get("id", "")
            page.session.store.set("current_generation_id", generation_id)

            # 3. Create checkout and redirect to Stripe
            checkout_result = await start_checkout(api, page, generation_id)
            if "error" in checkout_result:
                is_generating = False
                validation_error = checkout_result["error"]
                await _rebuild_step()
                return

            # Stripe redirect happened via launch_url — user will come back after payment

        except Exception as exc:
            is_generating = False
            validation_error = str(exc) or t("error.generic", lang)
            await _rebuild_step()

    # --- Step builders ---
    def _build_step1() -> ft.Control:
        """Upload selfies step."""
        # Upload zone
        upload_icon = ft.Icon(ft.Icons.CAMERA_ALT, size=48, color=T.TEXT_DISABLED)
        upload_title = ft.Text(
            t("create.upload_title", lang),
            size=T.FONT_H3,
            weight=ft.FontWeight.W600,
            color=T.TEXT_PRIMARY,
            text_align=ft.TextAlign.CENTER,
        )
        upload_desc = ft.Text(
            t("create.upload_desc", lang),
            size=T.FONT_BODY,
            color=T.TEXT_SECONDARY,
            text_align=ft.TextAlign.CENTER,
        )
        choose_btn = ft.ElevatedButton(
            text=t("create.upload_button", lang),
            icon=ft.Icons.ADD_PHOTO_ALTERNATE,
            bgcolor=T.PRIMARY,
            color=T.TEXT_ON_PRIMARY,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                padding=ft.padding.symmetric(horizontal=T.SPACE_LG, vertical=T.SPACE_MD),
            ),
            on_click=lambda _: file_picker.pick_files(
                allow_multiple=True,
                allowed_extensions=["jpg", "jpeg", "png"],
                dialog_title=t("create.upload_button", lang),
            ),
        )

        upload_zone = ft.Container(
            content=ft.Column(
                controls=[upload_icon, upload_title, upload_desc, choose_btn],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=T.SPACE_MD,
            ),
            width=min(500, page_width - 2 * h_pad),
            padding=ft.padding.all(T.SPACE_XXL),
            border=ft.border.all(2, T.OUTLINE_VARIANT),
            border_radius=T.RADIUS_LG,
            alignment=ft.alignment.center,
            bgcolor=T.SURFACE_VARIANT,
        )

        controls: list[ft.Control] = [upload_zone]

        # Show selected files as chips
        if selected_files:
            file_chips: list[ft.Control] = []
            for f in selected_files:
                file_chips.append(
                    ft.Chip(
                        label=ft.Text(f["name"], size=T.FONT_SMALL),
                        bgcolor=T.PRIMARY_CONTAINER,
                        delete_icon=ft.Icons.CLOSE,
                        on_delete=make_remove_handler(f["name"]),
                    )
                )
            controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=file_chips,
                        wrap=True,
                        spacing=T.SPACE_SM,
                        run_spacing=T.SPACE_SM,
                    ),
                    padding=ft.padding.only(top=T.SPACE_MD),
                    width=min(500, page_width - 2 * h_pad),
                )
            )
            controls.append(
                ft.Text(
                    t("create.uploaded_count", lang, count=len(selected_files)),
                    size=T.FONT_CAPTION,
                    color=T.TEXT_SECONDARY,
                )
            )

        # Validation error
        if validation_error:
            controls.append(
                ft.Text(
                    validation_error,
                    size=T.FONT_CAPTION,
                    color=T.ERROR,
                    text_align=ft.TextAlign.CENTER,
                )
            )

        # Continue button
        can_continue = len(selected_files) >= 2
        controls.append(
            ft.Container(
                content=ft.ElevatedButton(
                    text=t("common.continue", lang),
                    icon=ft.Icons.ARROW_FORWARD,
                    bgcolor=T.SECONDARY if can_continue else T.TEXT_DISABLED,
                    color=T.TEXT_ON_SECONDARY if can_continue else T.SURFACE,
                    disabled=not can_continue,
                    on_click=go_next,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                        padding=ft.padding.symmetric(horizontal=T.SPACE_XL, vertical=T.SPACE_MD),
                    ),
                ),
                padding=ft.padding.only(top=T.SPACE_LG),
            )
        )

        return ft.Column(
            controls=controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_SM,
        )

    def _build_step2() -> ft.Control:
        """Choose style step."""
        title = ft.Text(
            t("create.style_title", lang),
            size=T.FONT_H3,
            weight=ft.FontWeight.W600,
            color=T.TEXT_PRIMARY,
            text_align=ft.TextAlign.CENTER,
        )

        # Determine grid columns based on width
        if is_mobile:
            cols = 1
        elif page_width < T.TABLET_MAX:
            cols = 2
        else:
            cols = 3

        cards: list[ft.Control] = []
        for style_key in _STYLES:
            is_selected = selected_style == style_key
            style_color = T.STYLE_COLORS.get(style_key, T.PRIMARY)
            style_icon_name = T.STYLE_ICONS.get(style_key, "star")

            # Map string icon names to ft.Icons
            icon_map = {
                "business_center": ft.Icons.BUSINESS_CENTER,
                "local_hospital": ft.Icons.LOCAL_HOSPITAL,
                "account_balance": ft.Icons.ACCOUNT_BALANCE,
                "rocket_launch": ft.Icons.ROCKET_LAUNCH,
                "emoji_people": ft.Icons.EMOJI_PEOPLE,
                "computer": ft.Icons.COMPUTER,
            }
            icon_ref = icon_map.get(style_icon_name, ft.Icons.STAR)

            card_border = ft.border.all(3, T.SECONDARY) if is_selected else ft.border.all(1, T.OUTLINE_VARIANT)

            checkmark = ft.Container(
                content=ft.Icon(ft.Icons.CHECK_CIRCLE, color=T.SECONDARY, size=24),
                alignment=ft.alignment.top_right,
                padding=ft.padding.all(T.SPACE_SM),
                visible=is_selected,
            )

            color_band = ft.Container(
                bgcolor=style_color,
                height=6,
                border_radius=ft.border_radius.only(
                    top_left=T.RADIUS_MD, top_right=T.RADIUS_MD,
                ),
            )

            card_content = ft.Column(
                controls=[
                    color_band,
                    ft.Stack(
                        controls=[
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Icon(icon_ref, size=36, color=style_color),
                                        ft.Text(
                                            t(f"style.{style_key}", lang),
                                            size=T.FONT_H4,
                                            weight=ft.FontWeight.W600,
                                            color=T.TEXT_PRIMARY,
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                        ft.Text(
                                            t(f"style.{style_key}.desc", lang),
                                            size=T.FONT_CAPTION,
                                            color=T.TEXT_SECONDARY,
                                            text_align=ft.TextAlign.CENTER,
                                            max_lines=2,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=T.SPACE_SM,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                                padding=ft.padding.all(T.SPACE_MD),
                            ),
                            checkmark,
                        ],
                    ),
                ],
                spacing=0,
            )

            card = ft.Container(
                content=card_content,
                border=card_border,
                border_radius=T.RADIUS_MD,
                bgcolor=T.SURFACE,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                on_click=make_style_handler(style_key),
                ink=True,
                animate=ft.animation.Animation(T.ANIM_FAST, ft.AnimationCurve.EASE_IN_OUT),
            )

            cards.append(card)

        # Build responsive grid
        grid = ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=card,
                    col={"xs": 12, "sm": 6, "md": 4},
                )
                for card in cards
            ],
            spacing=T.SPACE_MD,
            run_spacing=T.SPACE_MD,
        )

        # Navigation buttons
        nav_row = ft.Row(
            controls=[
                ft.OutlinedButton(
                    text=t("common.back", lang),
                    icon=ft.Icons.ARROW_BACK,
                    on_click=go_back,
                    style=ft.ButtonStyle(
                        color=T.TEXT_SECONDARY,
                        side=ft.BorderSide(1, T.OUTLINE),
                        shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                        padding=ft.padding.symmetric(horizontal=T.SPACE_LG, vertical=T.SPACE_MD),
                    ),
                ),
                ft.ElevatedButton(
                    text=t("common.continue", lang),
                    icon=ft.Icons.ARROW_FORWARD,
                    bgcolor=T.SECONDARY if selected_style else T.TEXT_DISABLED,
                    color=T.TEXT_ON_SECONDARY if selected_style else T.SURFACE,
                    disabled=not selected_style,
                    on_click=go_next,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                        padding=ft.padding.symmetric(horizontal=T.SPACE_LG, vertical=T.SPACE_MD),
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        return ft.Column(
            controls=[title, grid, nav_row],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_LG,
        )

    def _build_step3() -> ft.Control:
        """Presentation selection + generate step."""
        title = ft.Text(
            t("create.presentation_title", lang),
            size=T.FONT_H3,
            weight=ft.FontWeight.W600,
            color=T.TEXT_PRIMARY,
            text_align=ft.TextAlign.CENTER,
        )

        presentations = [
            ("masculine", ft.Icons.MALE, "create.presentation_masculine"),
            ("feminine", ft.Icons.FEMALE, "create.presentation_feminine"),
        ]

        pres_cards: list[ft.Control] = []
        for pres_key, pres_icon, pres_label_key in presentations:
            is_selected = selected_presentation == pres_key
            card_bg = T.PRIMARY_CONTAINER if is_selected else T.SURFACE
            card_border = ft.border.all(2, T.PRIMARY) if is_selected else ft.border.all(1, T.OUTLINE_VARIANT)

            card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            pres_icon,
                            size=48,
                            color=T.PRIMARY if is_selected else T.TEXT_SECONDARY,
                        ),
                        ft.Text(
                            t(pres_label_key, lang),
                            size=T.FONT_H4,
                            weight=ft.FontWeight.W600,
                            color=T.PRIMARY if is_selected else T.TEXT_PRIMARY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=T.SPACE_MD,
                ),
                width=180 if not is_mobile else (page_width - 3 * h_pad) / 2,
                height=160,
                padding=ft.padding.all(T.SPACE_LG),
                border=card_border,
                border_radius=T.RADIUS_MD,
                bgcolor=card_bg,
                alignment=ft.alignment.center,
                on_click=make_presentation_handler(pres_key),
                ink=True,
                animate=ft.animation.Animation(T.ANIM_FAST, ft.AnimationCurve.EASE_IN_OUT),
            )
            pres_cards.append(card)

        pres_row = ft.Row(
            controls=pres_cards,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=T.SPACE_LG,
        )

        # Validation error
        error_text = ft.Text(
            validation_error or "",
            size=T.FONT_CAPTION,
            color=T.ERROR,
            text_align=ft.TextAlign.CENTER,
            visible=bool(validation_error),
        )

        # Generate button
        can_generate = bool(selected_presentation)
        generate_btn = ft.ElevatedButton(
            text=t("create.generate", lang),
            icon=ft.Icons.AUTO_AWESOME,
            bgcolor=T.SECONDARY if can_generate else T.TEXT_DISABLED,
            color=T.TEXT_ON_SECONDARY if can_generate else T.SURFACE,
            disabled=not can_generate,
            on_click=on_generate,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                padding=ft.padding.symmetric(horizontal=T.SPACE_XL, vertical=T.SPACE_MD),
                text_style=ft.TextStyle(size=T.FONT_H4, weight=ft.FontWeight.W600),
            ),
        )

        stripe_note = ft.Text(
            t("create.stripe_note", lang),
            size=T.FONT_SMALL,
            color=T.TEXT_DISABLED,
            text_align=ft.TextAlign.CENTER,
            italic=True,
        )

        # Back button
        back_btn = ft.OutlinedButton(
            text=t("common.back", lang),
            icon=ft.Icons.ARROW_BACK,
            on_click=go_back,
            style=ft.ButtonStyle(
                color=T.TEXT_SECONDARY,
                side=ft.BorderSide(1, T.OUTLINE),
                shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                padding=ft.padding.symmetric(horizontal=T.SPACE_LG, vertical=T.SPACE_MD),
            ),
        )

        return ft.Column(
            controls=[
                title,
                ft.Container(height=T.SPACE_MD),
                pres_row,
                error_text,
                ft.Container(height=T.SPACE_LG),
                generate_btn,
                stripe_note,
                ft.Container(height=T.SPACE_MD),
                back_btn,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_SM,
        )

    def _build_generating() -> ft.Control:
        """Generation in progress view."""
        return ft.Column(
            controls=[
                ft.Container(height=T.SPACE_HERO),
                ft.ProgressRing(
                    width=64,
                    height=64,
                    stroke_width=4,
                    color=T.SECONDARY,
                ),
                ft.Text(
                    t("create.generating", lang),
                    size=T.FONT_H3,
                    weight=ft.FontWeight.W600,
                    color=T.TEXT_PRIMARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    t("create.generating_desc", lang),
                    size=T.FONT_BODY,
                    color=T.TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=T.SPACE_HERO),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_MD,
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def _build_current_step() -> ft.Control:
        """Return the content for the current step."""
        if is_generating:
            return _build_generating()
        if current_step == 1:
            return _build_step1()
        if current_step == 2:
            return _build_step2()
        return _build_step3()

    async def _rebuild_step():
        """Rebuild the step content and update the page."""
        step_content = _build_current_step()
        progress = _build_progress_tracker(current_step, lang) if not is_generating else ft.Container()

        new_controls = [
            build_navbar(page),
            ft.Container(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                t("create.title", lang),
                                size=T.FONT_H1,
                                weight=ft.FontWeight.BOLD,
                                color=T.TEXT_PRIMARY,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            progress,
                            step_content,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=T.SPACE_MD,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    width=T.MAX_WIDTH,
                    padding=ft.padding.symmetric(
                        horizontal=h_pad,
                        vertical=T.SPACE_LG,
                    ),
                ),
                expand=True,
                bgcolor=T.BACKGROUND,
                alignment=ft.alignment.top_center,
            ),
            _build_footer(lang),
        ]

        view.controls = new_controls
        page.update()

    # --- Build initial view ---
    progress = _build_progress_tracker(current_step, lang)
    step_content = _build_current_step()

    page_title = ft.Text(
        t("create.title", lang),
        size=T.FONT_H1,
        weight=ft.FontWeight.BOLD,
        color=T.TEXT_PRIMARY,
        text_align=ft.TextAlign.CENTER,
    )

    body = ft.Container(
        content=ft.Container(
            content=ft.Column(
                controls=[page_title, progress, step_content],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=T.SPACE_MD,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=T.MAX_WIDTH,
            padding=ft.padding.symmetric(
                horizontal=h_pad,
                vertical=T.SPACE_LG,
            ),
        ),
        expand=True,
        bgcolor=T.BACKGROUND,
        alignment=ft.alignment.top_center,
    )

    view = ft.View(
        route="/create",
        controls=[
            build_navbar(page),
            body,
            _build_footer(lang),
        ],
        bgcolor=T.BACKGROUND,
        padding=0,
        spacing=0,
    )

    return view
