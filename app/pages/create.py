"""StudioFace Create Page — Dark premium 3-step wizard with real API calls."""

import flet as ft

try:
    import flet_camera as fc

    HAS_CAMERA = True
except ImportError:
    HAS_CAMERA = False

from app.components.navbar import build_navbar
from app.i18n import t
from app.services.upload_service import (
    create_session_and_upload,
    validate_file,
    validate_file_count,
)
from app.theme import StudioFaceTheme as T

# Style keys matching theme and i18n
_STYLES = ["corporate", "medical", "banking", "startup", "casual", "tech"]


def _build_progress_tracker(current_step: int, lang: str) -> ft.Control:
    """Build the 3-step progress indicator with gold active state."""
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
            circle_content = ft.Icon(ft.Icons.CHECK, color=T.TEXT_WHITE, size=18)
        elif is_active:
            circle_bg = T.PRIMARY_CONTAINER
            circle_content = ft.Text(
                str(num), color=T.ON_PRIMARY, size=T.FONT_CAPTION,
                weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,
            )
        else:
            circle_bg = T.BG_SURFACE_HIGH
            circle_content = ft.Text(
                str(num), color=T.TEXT_MUTED, size=T.FONT_CAPTION,
                text_align=ft.TextAlign.CENTER,
            )

        circle = ft.Container(
            content=circle_content,
            width=36,
            height=36,
            border_radius=18,
            bgcolor=circle_bg,
            alignment=ft.Alignment.CENTER,
        )

        label = ft.Text(
            t(key, lang),
            size=T.FONT_SMALL,
            color=T.PRIMARY if is_active else (T.SUCCESS if is_done else T.TEXT_MUTED),
            weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.W_400,
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
            line_color = T.SUCCESS if num < current_step else T.BG_SURFACE_HIGH
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


def _build_create_footer(lang: str) -> ft.Control:
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


def build(page: ft.Page) -> list[ft.Control]:
    """Build the Create page with a 3-step wizard. Returns list[ft.Control]."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX
    h_pad = T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING

    # --- Mutable wizard state ---
    state = {
        "current_step": 1,
        "selected_files": [],
        "selected_style": None,
        "selected_presentation": None,
        "validation_error": None,
        "is_generating": False,
        "upload_mode": "files",  # "files" or "camera"
        "camera_ready": False,
        "cameras": [],
        "current_camera_idx": 0,
        "is_uploading": False,
        "upload_session_id": None,
        "upload_ids": [],
    }

    # --- File picker setup (Flet 0.82: FilePicker is a Service, not a Control) ---
    # Created here but auto-registers via Service.init() with the page context.
    file_picker = ft.FilePicker()

    def on_pick_files_click(e):
        """Trigger async file picker."""
        async def do_pick():
            result = await file_picker.pick_files(
                allow_multiple=True,
                allowed_extensions=["jpg", "jpeg", "png"],
                dialog_title=t("create.upload_button", lang),
                file_type=ft.FilePickerFileType.CUSTOM,
                with_data=True,
            )
            if not result:
                return

            state["validation_error"] = None
            for f in result:
                if len(state["selected_files"]) >= 5:
                    state["validation_error"] = t("create.max_photos", lang)
                    break

                err = validate_file(f.name, f.size)
                if err:
                    state["validation_error"] = t(err, lang)
                    continue

                file_bytes = f.bytes
                if file_bytes is None and f.path:
                    try:
                        with open(f.path, "rb") as fh:
                            file_bytes = fh.read()
                    except Exception:
                        state["validation_error"] = t("error.upload_failed", lang)
                        continue

                if file_bytes is None:
                    state["validation_error"] = t("error.upload_failed", lang)
                    continue

                if any(sf["name"] == f.name for sf in state["selected_files"]):
                    continue

                state["selected_files"].append({
                    "name": f.name,
                    "size": f.size,
                    "bytes": file_bytes,
                })

            _rebuild_step()

        page.run_task(do_pick)

    # FilePicker auto-registers as a Service — no overlay needed

    # --- Camera setup (flet-camera, web/iOS/Android only) ---
    camera = None
    if HAS_CAMERA:
        camera = fc.Camera(
            preview_enabled=True,
            expand=True,
            height=300,
            width=400,
            visible=False,
        )

    def on_camera_mode(e):
        """Switch between file upload and camera mode."""
        state["upload_mode"] = "camera"
        state["validation_error"] = None
        _rebuild_step()
        if camera and not state["camera_ready"]:
            async def init_cam():
                try:
                    cams = await camera.get_available_cameras()
                    state["cameras"] = cams
                    if cams:
                        front = [c for c in cams if c.lens_direction == fc.CameraLensDirection.FRONT]
                        initial = front[0] if front else cams[0]
                        state["current_camera_idx"] = cams.index(initial)
                        await camera.initialize(
                            description=initial,
                            resolution_preset=fc.ResolutionPreset.HIGH,
                        )
                        state["camera_ready"] = True
                        camera.visible = True
                        page.update()
                except Exception:
                    state["upload_mode"] = "files"
                    state["validation_error"] = t("create.camera_not_available", lang)
                    _rebuild_step()
            page.run_task(init_cam)

    def on_files_mode(e):
        """Switch back to file upload mode."""
        state["upload_mode"] = "files"
        state["validation_error"] = None
        if camera:
            camera.visible = False
        _rebuild_step()

    def on_flip_camera(e):
        """Switch between front and back camera."""
        if not state["cameras"] or len(state["cameras"]) < 2:
            return
        async def do_flip():
            idx = (state["current_camera_idx"] + 1) % len(state["cameras"])
            state["current_camera_idx"] = idx
            await camera.initialize(
                description=state["cameras"][idx],
                resolution_preset=fc.ResolutionPreset.HIGH,
            )
            page.update()
        page.run_task(do_flip)

    def on_capture(e):
        """Capture a photo from the camera."""
        if len(state["selected_files"]) >= 5:
            state["validation_error"] = t("create.max_photos", lang)
            _rebuild_step()
            return
        async def do_capture():
            try:
                image_bytes = await camera.take_picture()
                if image_bytes:
                    idx = len(state["selected_files"]) + 1
                    state["selected_files"].append({
                        "name": f"camera_{idx}.jpg",
                        "size": len(image_bytes),
                        "bytes": image_bytes,
                    })
                    state["validation_error"] = None
                    _rebuild_step()
            except Exception:
                state["validation_error"] = t("error.upload_failed", lang)
                _rebuild_step()
        page.run_task(do_capture)

    # --- Navigation handlers ---
    def go_next(e):
        if state["current_step"] == 1:
            count_err = validate_file_count(len(state["selected_files"]))
            if count_err:
                state["validation_error"] = t(count_err, lang)
                _rebuild_step()
                return
            state["validation_error"] = None
            state["current_step"] = 2
        elif state["current_step"] == 2:
            if not state["selected_style"]:
                return
            state["current_step"] = 3
        _rebuild_step()

    def go_back(e):
        if state["current_step"] > 1:
            state["current_step"] -= 1
            _rebuild_step()

    def make_remove_handler(filename: str):
        def handler(e):
            state["selected_files"] = [
                f for f in state["selected_files"] if f["name"] != filename
            ]
            state["validation_error"] = None
            _rebuild_step()
        return handler

    def make_style_handler(style: str):
        def handler(e):
            state["selected_style"] = style
            _rebuild_step()
        return handler

    def make_presentation_handler(pres: str):
        def handler(e):
            state["selected_presentation"] = pres
            _rebuild_step()
        return handler

    def on_generate(e):
        if (
            not state["selected_style"]
            or not state["selected_presentation"]
            or len(state["selected_files"]) < 2
        ):
            return

        state["is_generating"] = True
        state["is_uploading"] = True
        _rebuild_step()

        async def do_generate():
            api = page.session.store.get("api")
            if not api:
                state["is_generating"] = False
                state["is_uploading"] = False
                state["validation_error"] = t("error.generic", lang)
                _rebuild_step()
                return

            # Step 1: Upload files
            files_to_upload = [
                (f["name"], f["bytes"]) for f in state["selected_files"]
            ]
            upload_result = await create_session_and_upload(api, files_to_upload)

            if "error" in upload_result:
                state["is_generating"] = False
                state["is_uploading"] = False
                state["validation_error"] = upload_result.get(
                    "error", t("error.upload_failed", lang)
                )
                _rebuild_step()
                return

            session_id = upload_result.get("session_id", "")
            upload_ids = upload_result.get("upload_ids", [])
            state["upload_session_id"] = session_id
            state["upload_ids"] = upload_ids
            state["is_uploading"] = False
            _rebuild_step()

            # Step 2: Create generation
            gen_result = await api.create_generation(
                style=state["selected_style"].upper(),
                upload_ids=upload_ids,
                presentation=state["selected_presentation"],
                upload_session_id=session_id,
            )

            if "error" in gen_result:
                state["is_generating"] = False
                state["validation_error"] = gen_result.get(
                    "error", t("error.generation_failed", lang)
                )
                _rebuild_step()
                return

            generation_id = gen_result.get("id", "")

            # Check if admin user — skip payment
            user = page.session.store.get("user")
            is_admin = False
            if isinstance(user, dict):
                is_admin = user.get("is_admin", False) or user.get("role") == "admin"

            if is_admin:
                state["is_generating"] = False
                page.go(f"/gallery?generation_id={generation_id}")
                return

            # Step 3: Create checkout
            checkout_result = await api.create_checkout(
                generation_id=generation_id,
                currency="EUR",
            )

            if "error" in checkout_result:
                state["is_generating"] = False
                state["validation_error"] = checkout_result.get(
                    "error", t("error.generic", lang)
                )
                _rebuild_step()
                return

            checkout_url = checkout_result.get("checkout_url", "")
            if checkout_url:
                page.launch_url(checkout_url)
            else:
                state["is_generating"] = False
                state["validation_error"] = t("error.generic", lang)
                _rebuild_step()

        page.run_task(do_generate)

    # --- Step builders ---
    def _build_step1() -> ft.Control:
        """Upload selfies step with file upload + camera toggle."""
        selected_files = state["selected_files"]
        validation_error = state["validation_error"]
        upload_mode = state["upload_mode"]

        # --- Mode toggle: Upload Files / Take Photo ---
        mode_toggle_controls = [
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.UPLOAD_FILE, size=18,
                                color=T.BUTTON_TEXT if upload_mode == "files" else T.TEXT_SECONDARY),
                        ft.Text(t("create.upload_files", lang), size=T.FONT_CAPTION,
                                color=T.BUTTON_TEXT if upload_mode == "files" else T.TEXT_SECONDARY),
                    ],
                    spacing=T.SPACE_SM,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                bgcolor=T.BUTTON_PRIMARY_BG if upload_mode == "files" else T.BG_SURFACE_HIGH,
                border_radius=T.RADIUS_SM,
                padding=ft.padding.symmetric(horizontal=T.SPACE_LG, vertical=T.SPACE_SM),
                on_click=on_files_mode,
                expand=True,
            ),
        ]
        if HAS_CAMERA:
            mode_toggle_controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CAMERA_ALT, size=18,
                                    color=T.BUTTON_TEXT if upload_mode == "camera" else T.TEXT_SECONDARY),
                            ft.Text(t("create.take_photo", lang), size=T.FONT_CAPTION,
                                    color=T.BUTTON_TEXT if upload_mode == "camera" else T.TEXT_SECONDARY),
                        ],
                        spacing=T.SPACE_SM,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    bgcolor=T.BUTTON_PRIMARY_BG if upload_mode == "camera" else T.BG_SURFACE_HIGH,
                    border_radius=T.RADIUS_SM,
                    padding=ft.padding.symmetric(horizontal=T.SPACE_LG, vertical=T.SPACE_SM),
                    on_click=on_camera_mode,
                    expand=True,
                ),
            )

        mode_toggle = ft.Container(
            content=ft.Row(
                controls=mode_toggle_controls,
                spacing=T.SPACE_SM,
            ),
            width=min(500, page_width - 2 * h_pad),
            padding=ft.padding.only(bottom=T.SPACE_MD),
        )

        # --- File upload zone (shown when mode == "files") ---
        upload_icon = ft.Icon(ft.Icons.UPLOAD_FILE, size=48, color=T.TEXT_MUTED)
        upload_title = ft.Text(
            t("create.upload_title", lang),
            size=T.FONT_H3,
            weight=ft.FontWeight.W_600,
            color=T.TEXT_WHITE,
            text_align=ft.TextAlign.CENTER,
        )
        upload_desc = ft.Text(
            t("create.upload_desc", lang),
            size=T.FONT_BODY,
            color=T.TEXT_SECONDARY,
            text_align=ft.TextAlign.CENTER,
        )
        choose_btn = ft.ElevatedButton(
            t("create.upload_button", lang),
            icon=ft.Icons.ADD_PHOTO_ALTERNATE,
            bgcolor=T.BUTTON_PRIMARY_BG,
            color=T.BUTTON_TEXT,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                padding=ft.padding.symmetric(horizontal=T.SPACE_LG, vertical=T.SPACE_MD),
            ),
            on_click=on_pick_files_click,
        )

        upload_zone = ft.Container(
            content=ft.Column(
                controls=[upload_icon, upload_title, upload_desc, choose_btn],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=T.SPACE_MD,
            ),
            width=min(500, page_width - 2 * h_pad),
            padding=ft.padding.all(T.SPACE_XXL),
            border=ft.border.all(2, T.OUTLINE),
            border_radius=T.RADIUS_LG,
            alignment=ft.Alignment.CENTER,
            bgcolor=T.BG_SURFACE,
            visible=(upload_mode == "files"),
        )

        # --- Camera zone (shown when mode == "camera") ---
        camera_zone_controls: list[ft.Control] = []
        if HAS_CAMERA and upload_mode == "camera":
            if state["camera_ready"] and camera:
                camera_zone_controls = [
                    ft.Container(
                        content=camera,
                        width=min(400, page_width - 2 * h_pad),
                        height=300,
                        border_radius=T.RADIUS_MD,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        bgcolor=T.BG_SURFACE_HIGH,
                    ),
                    ft.Row(
                        controls=[
                            ft.OutlinedButton(
                                t("create.flip_camera", lang),
                                icon=ft.Icons.FLIP_CAMERA_ANDROID,
                                style=ft.ButtonStyle(
                                    color=T.TEXT_SECONDARY,
                                    side=ft.BorderSide(1, T.OUTLINE),
                                    shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                                ),
                                on_click=on_flip_camera,
                                visible=len(state["cameras"]) > 1,
                            ),
                            ft.ElevatedButton(
                                t("create.capture", lang),
                                icon=ft.Icons.CAMERA,
                                bgcolor=T.BUTTON_PRIMARY_BG,
                                color=T.BUTTON_TEXT,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                                    padding=ft.padding.symmetric(
                                        horizontal=T.SPACE_LG, vertical=T.SPACE_MD
                                    ),
                                ),
                                on_click=on_capture,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=T.SPACE_MD,
                    ),
                ]
            else:
                camera_zone_controls = [
                    ft.ProgressRing(width=32, height=32, color=T.PRIMARY),
                    ft.Text(
                        t("create.camera_initializing", lang),
                        size=T.FONT_BODY,
                        color=T.TEXT_SECONDARY,
                    ),
                ]

        camera_zone = ft.Container(
            content=ft.Column(
                controls=camera_zone_controls,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=T.SPACE_MD,
            ),
            width=min(500, page_width - 2 * h_pad),
            padding=ft.padding.all(T.SPACE_XXL),
            border=ft.border.all(2, T.OUTLINE),
            border_radius=T.RADIUS_LG,
            alignment=ft.Alignment.CENTER,
            bgcolor=T.BG_SURFACE,
            visible=(upload_mode == "camera"),
        )

        controls: list[ft.Control] = [mode_toggle, upload_zone, camera_zone]

        if selected_files:
            file_chips: list[ft.Control] = []
            for f in selected_files:
                file_chips.append(
                    ft.Chip(
                        label=ft.Text(f["name"], size=T.FONT_SMALL),
                        bgcolor=T.BG_SURFACE_HIGH,
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

        if validation_error:
            controls.append(
                ft.Text(
                    validation_error,
                    size=T.FONT_CAPTION,
                    color=T.ERROR,
                    text_align=ft.TextAlign.CENTER,
                )
            )

        can_continue = len(selected_files) >= 2
        controls.append(
            ft.Container(
                content=ft.ElevatedButton(
                    t("common.continue", lang),
                    icon=ft.Icons.ARROW_FORWARD,
                    bgcolor=T.BUTTON_PRIMARY_BG if can_continue else T.TEXT_DISABLED,
                    color=T.BUTTON_TEXT if can_continue else T.BG_SURFACE,
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
        """Choose style step with real photos."""
        selected_style = state["selected_style"]

        title = ft.Text(
            t("create.style_title", lang),
            size=T.FONT_H3,
            weight=ft.FontWeight.W_600,
            color=T.TEXT_WHITE,
            text_align=ft.TextAlign.CENTER,
        )

        cards: list[ft.Control] = []
        for style_key in _STYLES:
            is_selected = selected_style == style_key
            photo_url = T.STYLE_PHOTOS.get(style_key, "")

            card_border = (
                ft.border.all(3, T.PRIMARY_CONTAINER)
                if is_selected
                else ft.border.all(1, T.BORDER)
            )

            # Image area
            if photo_url:
                image_area = ft.Container(
                    content=ft.Image(
                        src=photo_url,
                        fit=ft.BoxFit.COVER,
                        height=120,
                    ),
                    height=120,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    border_radius=ft.border_radius.only(
                        top_left=T.RADIUS_MD,
                        top_right=T.RADIUS_MD,
                    ),
                )
            else:
                style_color = T.STYLE_COLORS.get(style_key, T.PRIMARY)
                image_area = ft.Container(
                    content=ft.Icon(ft.Icons.STAR, color=T.TEXT_WHITE, size=28),
                    height=120,
                    bgcolor=style_color,
                    border_radius=ft.border_radius.only(
                        top_left=T.RADIUS_MD,
                        top_right=T.RADIUS_MD,
                    ),
                    alignment=ft.Alignment.CENTER,
                )

            checkmark = ft.Container(
                content=ft.Icon(ft.Icons.CHECK_CIRCLE, color=T.PRIMARY_CONTAINER, size=24),
                alignment=ft.Alignment.TOP_RIGHT,
                padding=ft.padding.all(T.SPACE_SM),
                visible=is_selected,
            )

            card_content = ft.Column(
                controls=[
                    image_area,
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    t(f"style.{style_key}", lang),
                                    size=T.FONT_BODY,
                    weight=ft.FontWeight.W_600,
                                    color=T.TEXT_WHITE,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Text(
                                    t(f"style.{style_key}.desc", lang),
                                    size=T.FONT_SMALL,
                                    color=T.TEXT_SECONDARY,
                                    text_align=ft.TextAlign.CENTER,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=T.SPACE_XS,
                        ),
                        padding=ft.padding.all(T.SPACE_SM),
                    ),
                ],
                spacing=0,
            )

            card = ft.Container(
                content=ft.Stack(
                    controls=[card_content, checkmark],
                ),
                border=card_border,
                border_radius=T.RADIUS_MD,
                bgcolor=T.BG_SURFACE,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                on_click=make_style_handler(style_key),
                ink=True,
            )

            cards.append(card)

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

        nav_row = ft.Row(
            controls=[
                ft.OutlinedButton(
                    t("common.back", lang),
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
                    t("common.continue", lang),
                    icon=ft.Icons.ARROW_FORWARD,
                    bgcolor=T.BUTTON_PRIMARY_BG if selected_style else T.TEXT_DISABLED,
                    color=T.BUTTON_TEXT if selected_style else T.BG_SURFACE,
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
        selected_presentation = state["selected_presentation"]
        validation_error = state["validation_error"]

        title = ft.Text(
            t("create.presentation_title", lang),
            size=T.FONT_H3,
            weight=ft.FontWeight.W_600,
            color=T.TEXT_WHITE,
            text_align=ft.TextAlign.CENTER,
        )

        presentations = [
            ("masculine", ft.Icons.MALE, "create.presentation_masculine"),
            ("feminine", ft.Icons.FEMALE, "create.presentation_feminine"),
        ]

        pres_cards: list[ft.Control] = []
        for pres_key, pres_icon, pres_label_key in presentations:
            is_selected = selected_presentation == pres_key
            card_bg = T.BG_SURFACE_HIGH if is_selected else T.BG_SURFACE
            card_border = (
                ft.border.all(2, T.PRIMARY_CONTAINER)
                if is_selected
                else ft.border.all(1, T.BORDER)
            )

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
                            weight=ft.FontWeight.W_600,
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
                alignment=ft.Alignment.CENTER,
                on_click=make_presentation_handler(pres_key),
                ink=True,
            )
            pres_cards.append(card)

        pres_row = ft.Row(
            controls=pres_cards,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=T.SPACE_LG,
        )

        error_text = ft.Text(
            validation_error or "",
            size=T.FONT_CAPTION,
            color=T.ERROR,
            text_align=ft.TextAlign.CENTER,
            visible=bool(validation_error),
        )

        can_generate = bool(selected_presentation)
        generate_btn = ft.ElevatedButton(
            t("create.generate", lang),
            icon=ft.Icons.AUTO_AWESOME,
            bgcolor=T.BUTTON_PRIMARY_BG if can_generate else T.TEXT_DISABLED,
            color=T.BUTTON_TEXT if can_generate else T.BG_SURFACE,
            disabled=not can_generate,
            on_click=on_generate,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=T.RADIUS_SM),
                padding=ft.padding.symmetric(horizontal=T.SPACE_XL, vertical=T.SPACE_MD),
                text_style=ft.TextStyle(size=T.FONT_H4, weight=ft.FontWeight.W_600),
            ),
        )

        stripe_note = ft.Text(
            t("create.stripe_note", lang),
            size=T.FONT_SMALL,
            color=T.TEXT_MUTED,
            text_align=ft.TextAlign.CENTER,
            italic=True,
        )

        back_btn = ft.OutlinedButton(
            t("common.back", lang),
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
        if state["is_uploading"]:
            status_text = t("create.uploading", lang)
            sub_text = t("common.loading", lang)
        else:
            status_text = t("create.generating", lang)
            sub_text = t("create.generating_desc", lang)

        return ft.Column(
            controls=[
                ft.Container(height=T.SPACE_HERO),
                ft.ProgressRing(
                    width=64,
                    height=64,
                    stroke_width=4,
                    color=T.PRIMARY_CONTAINER,
                ),
                ft.Text(
                    status_text,
                    size=T.FONT_H3,
                    weight=ft.FontWeight.W_600,
                    color=T.TEXT_WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    sub_text,
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
        if state["is_generating"]:
            return _build_generating()
        if state["current_step"] == 1:
            return _build_step1()
        if state["current_step"] == 2:
            return _build_step2()
        return _build_step3()

    def _rebuild_step():
        current_step = state["current_step"]
        step_content = _build_current_step()
        progress = (
            _build_progress_tracker(current_step, lang)
            if not state["is_generating"]
            else ft.Container()
        )

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
                                color=T.TEXT_WHITE,
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
                bgcolor=T.BG_PRIMARY,
                alignment=ft.Alignment.TOP_CENTER,
            ),
            _build_create_footer(lang),
        ]

        page.controls.clear()
        page.controls.extend(new_controls)
        page.update()

    # --- Build initial controls ---
    progress = _build_progress_tracker(state["current_step"], lang)
    step_content = _build_current_step()

    page_title = ft.Text(
        t("create.title", lang),
        size=T.FONT_H1,
        weight=ft.FontWeight.BOLD,
        color=T.TEXT_WHITE,
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
        bgcolor=T.BG_PRIMARY,
        alignment=ft.Alignment.TOP_CENTER,
    )

    return [
        build_navbar(page),
        body,
        _build_create_footer(lang),
    ]
