"""StudioFace Landing Page — Dark premium design matching production."""

import flet as ft

from app.components.cookie_banner import build_cookie_banner
from app.components.footer import build_footer
from app.components.navbar import build_navbar
from app.i18n import t
from app.theme import StudioFaceTheme as T


def _build_hero(page: ft.Page) -> ft.Container:
    """Hero section with gold pill badge, large heading, subtitle, CTA, and trust bar."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    def on_cta_click(e):
        page.go("/create")

    # Gold pill badge
    badge = ft.Container(
        content=ft.Text(
            t("hero.badge", lang),
            size=T.FONT_SMALL,
            weight=ft.FontWeight.W_600,
            color=T.ON_PRIMARY,
        ),
        bgcolor=T.PRIMARY_CONTAINER,
        border_radius=T.RADIUS_PILL,
        padding=ft.padding.symmetric(horizontal=T.SPACE_MD, vertical=T.SPACE_XS),
    )

    # Large heading with gold italic accent word
    full_title = t("hero.title_dark", lang)
    accent_word = t("hero.title_accent", lang)

    # Split title around accent word
    if accent_word in full_title:
        parts = full_title.split(accent_word, 1)
        title_spans = [
            ft.TextSpan(
                parts[0],
                ft.TextStyle(
                    size=T.FONT_HERO if not is_mobile else T.FONT_H1,
                    weight=ft.FontWeight.BOLD,
                    color=T.TEXT_WHITE,
                ),
            ),
            ft.TextSpan(
                accent_word,
                ft.TextStyle(
                    size=T.FONT_HERO if not is_mobile else T.FONT_H1,
                    weight=ft.FontWeight.BOLD,
                    color=T.PRIMARY,
                    italic=True,
                ),
            ),
        ]
        if len(parts) > 1 and parts[1]:
            title_spans.append(
                ft.TextSpan(
                    parts[1],
                    ft.TextStyle(
                        size=T.FONT_HERO if not is_mobile else T.FONT_H1,
                        weight=ft.FontWeight.BOLD,
                        color=T.TEXT_WHITE,
                    ),
                ),
            )
        heading = ft.Text(
            spans=title_spans,
            text_align=ft.TextAlign.CENTER,
        )
    else:
        heading = ft.Text(
            full_title,
            size=T.FONT_HERO if not is_mobile else T.FONT_H1,
            weight=ft.FontWeight.BOLD,
            color=T.TEXT_WHITE,
            text_align=ft.TextAlign.CENTER,
        )

    # Price in heading
    price_line = ft.Text(
        "\u2014 Just \u20ac6.99",
        size=T.FONT_H2 if not is_mobile else T.FONT_H3,
        weight=ft.FontWeight.W_600,
        color=T.PRIMARY,
        text_align=ft.TextAlign.CENTER,
    )

    # Subtitle
    subtitle = ft.Text(
        t("hero.subtitle_dark", lang),
        size=T.FONT_BODY_LG if not is_mobile else T.FONT_BODY,
        color=T.TEXT_SECONDARY,
        text_align=ft.TextAlign.CENTER,
        width=600 if not is_mobile else None,
    )

    # Gold CTA button
    cta_button = ft.Container(
        content=ft.Text(
            t("hero.cta_dark", lang),
            size=T.FONT_BODY_LG,
            weight=ft.FontWeight.W_600,
            color=T.BUTTON_TEXT,
            text_align=ft.TextAlign.CENTER,
        ),
        bgcolor=T.BUTTON_PRIMARY_BG,
        border_radius=T.RADIUS_PILL,
        padding=ft.padding.symmetric(horizontal=T.SPACE_XL, vertical=T.SPACE_MD),
        on_click=on_cta_click,
    )

    # Trust bar
    trust_text = ft.Text(
        t("hero.trust", lang),
        size=T.FONT_SMALL,
        color=T.TEXT_MUTED,
        text_align=ft.TextAlign.CENTER,
    )

    hero_content = ft.Column(
        controls=[
            badge,
            ft.Container(height=T.SPACE_LG),
            heading,
            price_line,
            ft.Container(height=T.SPACE_MD),
            subtitle,
            ft.Container(height=T.SPACE_XL),
            cta_button,
            ft.Container(height=T.SPACE_MD),
            trust_text,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )

    return ft.Container(
        content=ft.Container(
            content=hero_content,
            width=T.MAX_WIDTH,
            padding=ft.padding.symmetric(
                horizontal=T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING,
                vertical=T.SPACE_SECTION if not is_mobile else T.SPACE_HERO,
            ),
            alignment=ft.Alignment.CENTER,
        ),
        bgcolor=T.BG_PRIMARY,
        alignment=ft.Alignment.CENTER,
    )


def _build_results_gallery(page: ft.Page) -> ft.Container:
    """Results gallery showing real customer photos."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    # Section label
    label = ft.Text(
        t("results.label", lang),
        size=T.FONT_LABEL,
        weight=ft.FontWeight.W_600,
        color=T.TEXT_SECONDARY,
        text_align=ft.TextAlign.CENTER,
    )

    # Photo cards
    photo_cards = []
    for photo in T.SAMPLE_PHOTOS:
        card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Image(
                            src=photo["url"],
                            fit=ft.BoxFit.COVER,
                            height=240 if not is_mobile else 180,
                            width=180 if not is_mobile else 140,
                            border_radius=T.RADIUS_MD,
                        ),
                        border_radius=T.RADIUS_MD,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    ),
                    ft.Text(
                        photo["name"],
                        size=T.FONT_CAPTION,
                        color=T.TEXT_WHITE,
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.W_500,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=T.SPACE_SM,
            ),
        )
        photo_cards.append(card)

    if is_mobile:
        photos_layout = ft.Row(
            controls=photo_cards,
            spacing=T.SPACE_MD,
            scroll=ft.ScrollMode.AUTO,
        )
    else:
        photos_layout = ft.Row(
            controls=photo_cards,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=T.SPACE_LG,
        )

    return ft.Container(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    label,
                    ft.Container(height=T.SPACE_XL),
                    photos_layout,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            width=T.MAX_WIDTH,
            padding=ft.padding.symmetric(
                horizontal=T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING,
                vertical=T.SPACE_HERO,
            ),
        ),
        bgcolor=T.BG_SURFACE,
        alignment=ft.Alignment.CENTER,
    )


def _build_how_it_works(page: ft.Page) -> ft.Container:
    """How It Works section with 3 dark cards."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    steps = [
        (ft.Icons.CAMERA_ALT, 1, t("features.step1.title", lang), t("features.step1.desc", lang)),
        (ft.Icons.PALETTE, 2, t("features.step2.title", lang), t("features.step2.desc", lang)),
        (ft.Icons.DOWNLOAD, 3, t("features.step3.title", lang), t("features.step3.desc", lang)),
    ]

    step_cards = []
    for icon, num, title, desc in steps:
        # Numbered circle
        num_circle = ft.Container(
            content=ft.Text(
                str(num),
                size=T.FONT_CAPTION,
                weight=ft.FontWeight.BOLD,
                color=T.ON_PRIMARY,
                text_align=ft.TextAlign.CENTER,
            ),
            width=32,
            height=32,
            bgcolor=T.PRIMARY_CONTAINER,
            border_radius=16,
            alignment=ft.Alignment.CENTER,
        )

        card = ft.Container(
            content=ft.Column(
                controls=[
                    num_circle,
                    ft.Container(height=T.SPACE_MD),
                    ft.Icon(icon, color=T.PRIMARY, size=32),
                    ft.Container(height=T.SPACE_MD),
                    ft.Text(
                        title,
                        size=T.FONT_H4,
                        weight=ft.FontWeight.W_600,
                        color=T.TEXT_WHITE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=T.SPACE_XS),
                    ft.Text(
                        desc,
                        size=T.FONT_CAPTION,
                        color=T.TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER,
                        width=240,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            bgcolor=T.BG_SURFACE,
            border_radius=T.RADIUS_LG,
            border=ft.border.all(1, T.BORDER),
            padding=T.CARD_PADDING,
            expand=1 if not is_mobile else None,
            width=None if not is_mobile else 320,
        )
        step_cards.append(card)

    if is_mobile:
        cards_layout = ft.Column(
            controls=step_cards,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_LG,
        )
    else:
        cards_layout = ft.Row(
            controls=step_cards,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=T.SPACE_LG,
        )

    return ft.Container(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        t("features.title", lang),
                        size=T.FONT_H1,
                        weight=ft.FontWeight.BOLD,
                        color=T.TEXT_WHITE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=T.SPACE_XL),
                    cards_layout,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            width=T.MAX_WIDTH,
            padding=ft.padding.symmetric(
                horizontal=T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING,
                vertical=T.SPACE_HERO,
            ),
        ),
        bgcolor=T.BG_SURFACE_HIGH,
        alignment=ft.Alignment.CENTER,
    )


def _build_style_showcase(page: ft.Page) -> ft.Container:
    """Style showcase section with 6 style cards using real photos."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    styles = ["corporate", "medical", "banking", "startup", "casual", "tech"]

    style_cards = []
    for style_key in styles:
        style_name = t(f"style.{style_key}", lang)
        style_desc = t(f"style.{style_key}.desc", lang)
        photo_url = T.STYLE_PHOTOS.get(style_key, "")

        # Card with real photo
        if photo_url:
            image_area = ft.Container(
                content=ft.Image(
                    src=photo_url,
                    fit=ft.BoxFit.COVER,
                    height=160,
                ),
                height=160,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                border_radius=ft.border_radius.only(
                    top_left=T.RADIUS_MD,
                    top_right=T.RADIUS_MD,
                ),
            )
        else:
            style_color = T.STYLE_COLORS.get(style_key, T.PRIMARY)
            image_area = ft.Container(
                content=ft.Icon(
                    T.STYLE_ICONS.get(style_key, "star"),
                    color=T.TEXT_WHITE,
                    size=32,
                ),
                height=160,
                bgcolor=style_color,
                border_radius=ft.border_radius.only(
                    top_left=T.RADIUS_MD,
                    top_right=T.RADIUS_MD,
                ),
                alignment=ft.Alignment.CENTER,
            )

        text_area = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        style_name,
                        size=T.FONT_BODY,
                        weight=ft.FontWeight.W_600,
                        color=T.TEXT_WHITE,
                    ),
                    ft.Text(
                        style_desc,
                        size=T.FONT_SMALL,
                        color=T.TEXT_SECONDARY,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
                spacing=T.SPACE_XS,
            ),
            padding=ft.padding.all(T.SPACE_MD),
        )

        card = ft.Container(
            content=ft.Column(
                controls=[image_area, text_area],
                spacing=0,
            ),
            bgcolor=T.BG_SURFACE,
            border=ft.border.all(1, T.BORDER),
            border_radius=T.RADIUS_MD,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            col={"xs": 12, "sm": 6, "md": 4},
        )
        style_cards.append(card)

    return ft.Container(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        t("styles.title", lang),
                        size=T.FONT_H1,
                        weight=ft.FontWeight.BOLD,
                        color=T.TEXT_WHITE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=T.SPACE_XL),
                    ft.ResponsiveRow(
                        controls=style_cards,
                        spacing=T.SPACE_LG,
                        run_spacing=T.SPACE_LG,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            width=T.MAX_WIDTH,
            padding=ft.padding.symmetric(
                horizontal=T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING,
                vertical=T.SPACE_HERO,
            ),
        ),
        bgcolor=T.BG_PRIMARY,
        alignment=ft.Alignment.CENTER,
    )


def _build_pricing(page: ft.Page) -> ft.Container:
    """Pricing section with dark card and gold accent."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    def on_buy_click(e):
        page.go("/create")

    # Features list
    features = [
        t("pricing.feature1", lang),
        t("pricing.feature2", lang),
        t("pricing.feature3", lang),
        t("pricing.feature4", lang),
    ]

    feature_items = []
    for feat in features:
        feature_items.append(
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=T.SUCCESS, size=20),
                    ft.Text(feat, size=T.FONT_BODY, color=T.TEXT_PRIMARY),
                ],
                spacing=T.SPACE_SM,
            )
        )

    pricing_card = ft.Container(
        content=ft.Column(
            controls=[
                # Strikethrough old price
                ft.Text(
                    "\u20ac24.99",
                    size=T.FONT_H4,
                    color=T.TEXT_MUTED,
                    text_align=ft.TextAlign.CENTER,
                    style=ft.TextStyle(
                        decoration=ft.TextDecoration.LINE_THROUGH,
                    ),
                ),
                # New price
                ft.Text(
                    t("pricing.price", lang),
                    size=T.FONT_HERO,
                    weight=ft.FontWeight.BOLD,
                    color=T.PRIMARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    t("pricing.per", lang),
                    size=T.FONT_BODY,
                    color=T.TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=T.SPACE_LG),
                ft.Divider(color=T.DIVIDER),
                ft.Container(height=T.SPACE_MD),
                *feature_items,
                ft.Container(height=T.SPACE_LG),
                # Gold CTA button
                ft.Container(
                    content=ft.Text(
                        t("pricing.cta", lang),
                        size=T.FONT_BODY,
                        weight=ft.FontWeight.W_600,
                        color=T.BUTTON_TEXT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    bgcolor=T.BUTTON_PRIMARY_BG,
                    border_radius=T.RADIUS_PILL,
                    padding=ft.padding.symmetric(horizontal=T.SPACE_XL, vertical=T.SPACE_MD),
                    on_click=on_buy_click,
                    alignment=ft.Alignment.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_SM,
        ),
        width=420,
        bgcolor=T.BG_SURFACE,
        border_radius=T.RADIUS_LG,
        padding=ft.padding.all(T.SPACE_XL),
        border=ft.border.all(1, T.BORDER),
    )

    return ft.Container(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        t("pricing.title", lang),
                        size=T.FONT_H1,
                        weight=ft.FontWeight.BOLD,
                        color=T.TEXT_WHITE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=T.SPACE_XL),
                    pricing_card,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            width=T.MAX_WIDTH,
            padding=ft.padding.symmetric(
                horizontal=T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING,
                vertical=T.SPACE_HERO,
            ),
        ),
        bgcolor=T.BG_SURFACE,
        alignment=ft.Alignment.CENTER,
    )


def build(page: ft.Page) -> list[ft.Control]:
    """Build the landing page — returns list of controls."""
    lang = page.session.store.get("lang") or "en"
    return [
        build_navbar(page),
        _build_hero(page),
        _build_results_gallery(page),
        _build_how_it_works(page),
        _build_style_showcase(page),
        _build_pricing(page),
        build_footer(page),
        build_cookie_banner(page, lang),
    ]
