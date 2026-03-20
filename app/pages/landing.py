"""StudioFace Landing Page — Hero, features, styles, pricing, trust bar."""

import flet as ft

from app.components.cookie_banner import build_cookie_banner
from app.components.footer import build_footer
from app.components.navbar import build_navbar
from app.i18n import t
from app.theme import StudioFaceTheme as T


def _build_hero(page: ft.Page) -> ft.Control:
    """Hero section with headline, subtitle, CTA, and social proof."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    def on_cta_click(e: ft.ControlEvent) -> None:
        page.go("/create")

    hero_content = ft.Column(
        controls=[
            ft.Text(
                t("hero.title", lang),
                size=T.FONT_HERO if not is_mobile else T.FONT_H1,
                weight=ft.FontWeight.BOLD,
                color=T.TEXT_ON_PRIMARY,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(height=T.SPACE_MD),
            ft.Text(
                t("hero.subtitle", lang),
                size=T.FONT_H3 if not is_mobile else T.FONT_H4,
                color=ft.Colors.with_opacity(0.85, T.TEXT_ON_PRIMARY),
                text_align=ft.TextAlign.CENTER,
                width=700 if not is_mobile else None,
            ),
            ft.Container(height=T.SPACE_XL),
            # CTA button
            ft.Container(
                content=ft.Text(
                    t("hero.cta", lang),
                    size=T.FONT_H4,
                    weight=ft.FontWeight.W600,
                    color=T.TEXT_ON_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                bgcolor=T.SECONDARY,
                border_radius=T.RADIUS_PILL,
                padding=ft.padding.symmetric(horizontal=T.SPACE_XL, vertical=T.SPACE_MD),
                on_click=on_cta_click,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=16,
                    color=ft.Colors.with_opacity(0.35, T.SECONDARY_DARK),
                    offset=ft.Offset(0, 4),
                ),
                animate=ft.Animation(T.ANIM_NORMAL, ft.AnimationCurve.EASE_IN_OUT),
            ),
            ft.Container(height=T.SPACE_LG),
            # Social proof
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.PEOPLE_OUTLINE, color=ft.Colors.with_opacity(0.7, T.TEXT_ON_PRIMARY), size=20),
                    ft.Text(
                        t("hero.photos_generated", lang, count="17,000+"),
                        size=T.FONT_CAPTION,
                        color=ft.Colors.with_opacity(0.7, T.TEXT_ON_PRIMARY),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=T.SPACE_SM,
            ),
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
                vertical=T.SPACE_HERO,
            ),
            alignment=ft.alignment.center,
        ),
        bgcolor=T.PRIMARY,
        alignment=ft.alignment.center,
    )


def _build_step_card(
    icon: str,
    step_number: int,
    title: str,
    description: str,
    is_mobile: bool,
) -> ft.Control:
    """Build a single 'How It Works' step card."""
    return ft.Container(
        content=ft.Column(
            controls=[
                # Step number badge
                ft.Container(
                    content=ft.Text(
                        str(step_number),
                        size=T.FONT_SMALL,
                        weight=ft.FontWeight.BOLD,
                        color=T.TEXT_ON_PRIMARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    width=28,
                    height=28,
                    bgcolor=T.SECONDARY,
                    border_radius=T.RADIUS_PILL,
                    alignment=ft.alignment.center,
                ),
                ft.Container(height=T.SPACE_MD),
                # Icon circle
                ft.Container(
                    content=ft.Icon(icon, color=T.PRIMARY, size=32),
                    width=64,
                    height=64,
                    bgcolor=T.PRIMARY_CONTAINER,
                    border_radius=T.RADIUS_PILL,
                    alignment=ft.alignment.center,
                ),
                ft.Container(height=T.SPACE_MD),
                # Title
                ft.Text(
                    title,
                    size=T.FONT_H4,
                    weight=ft.FontWeight.W600,
                    color=T.TEXT_PRIMARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=T.SPACE_XS),
                # Description
                ft.Text(
                    description,
                    size=T.FONT_CAPTION,
                    color=T.TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                    width=240,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        bgcolor=T.SURFACE,
        border_radius=T.RADIUS_MD,
        padding=T.CARD_PADDING,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
        expand=1 if not is_mobile else None,
        width=None if not is_mobile else 320,
    )


def _build_how_it_works(page: ft.Page) -> ft.Control:
    """How It Works section with 3 step cards."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    steps = [
        (ft.Icons.CAMERA_ALT, 1, t("features.step1.title", lang), t("features.step1.desc", lang)),
        (ft.Icons.PALETTE, 2, t("features.step2.title", lang), t("features.step2.desc", lang)),
        (ft.Icons.DOWNLOAD, 3, t("features.step3.title", lang), t("features.step3.desc", lang)),
    ]

    step_cards = [
        _build_step_card(icon, num, title, desc, is_mobile)
        for icon, num, title, desc in steps
    ]

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
                        color=T.TEXT_PRIMARY,
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
        bgcolor=T.BACKGROUND,
        alignment=ft.alignment.center,
    )


def _build_style_card(
    style_key: str,
    lang: str,
    is_mobile: bool,
) -> ft.Control:
    """Build a single style showcase card."""
    color = T.STYLE_COLORS.get(style_key, T.PRIMARY)
    style_name = t(f"style.{style_key}", lang)
    style_desc = t(f"style.{style_key}.desc", lang)

    return ft.Container(
        content=ft.Column(
            controls=[
                # Colored gradient header
                ft.Container(
                    content=ft.Icon(
                        T.STYLE_ICONS.get(style_key, "star"),
                        color=T.TEXT_ON_PRIMARY,
                        size=28,
                    ),
                    height=80,
                    bgcolor=color,
                    border_radius=ft.border_radius.only(
                        top_left=T.RADIUS_MD,
                        top_right=T.RADIUS_MD,
                    ),
                    alignment=ft.alignment.center,
                ),
                # Text content
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                style_name,
                                size=T.FONT_H4,
                                weight=ft.FontWeight.W600,
                                color=T.TEXT_PRIMARY,
                            ),
                            ft.Text(
                                style_desc,
                                size=T.FONT_CAPTION,
                                color=T.TEXT_SECONDARY,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=T.SPACE_XS,
                    ),
                    padding=ft.padding.all(T.SPACE_MD),
                ),
            ],
            spacing=0,
        ),
        bgcolor=T.SURFACE,
        border_radius=T.RADIUS_MD,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        col={"xs": 12, "sm": 6, "md": 4},
    )


def _build_style_showcase(page: ft.Page) -> ft.Control:
    """Style showcase section with 6 style cards in responsive grid."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    styles = ["corporate", "medical", "banking", "startup", "casual", "tech"]

    style_cards = [
        _build_style_card(style_key, lang, is_mobile)
        for style_key in styles
    ]

    return ft.Container(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        t("pricing.includes", lang),
                        size=T.FONT_H1,
                        weight=ft.FontWeight.BOLD,
                        color=T.TEXT_PRIMARY,
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
        bgcolor=T.SURFACE,
        alignment=ft.alignment.center,
    )


def _build_feature_item(text: str) -> ft.Control:
    """Build a pricing feature item with checkmark."""
    return ft.Row(
        controls=[
            ft.Icon(ft.Icons.CHECK_CIRCLE, color=T.SUCCESS, size=20),
            ft.Text(
                text,
                size=T.FONT_BODY,
                color=T.TEXT_PRIMARY,
            ),
        ],
        spacing=T.SPACE_SM,
    )


def _build_pricing(page: ft.Page) -> ft.Control:
    """Pricing section with a centered pricing card."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    def on_buy_click(e: ft.ControlEvent) -> None:
        page.go("/create")

    pricing_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    t("pricing.price", lang),
                    size=T.FONT_HERO,
                    weight=ft.FontWeight.BOLD,
                    color=T.PRIMARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    t("pricing.per", lang),
                    size=T.FONT_H4,
                    color=T.TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=T.SPACE_LG),
                ft.Divider(color=T.DIVIDER),
                ft.Container(height=T.SPACE_MD),
                _build_feature_item(t("pricing.feature1", lang)),
                _build_feature_item(t("pricing.feature2", lang)),
                _build_feature_item(t("pricing.feature3", lang)),
                _build_feature_item(t("pricing.feature4", lang)),
                ft.Container(height=T.SPACE_LG),
                # CTA button
                ft.Container(
                    content=ft.Text(
                        t("pricing.cta", lang),
                        size=T.FONT_BODY,
                        weight=ft.FontWeight.W600,
                        color=T.TEXT_ON_SECONDARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    bgcolor=T.SECONDARY,
                    border_radius=T.RADIUS_PILL,
                    padding=ft.padding.symmetric(horizontal=T.SPACE_XL, vertical=T.SPACE_MD),
                    on_click=on_buy_click,
                    alignment=ft.alignment.center,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=8,
                        color=ft.Colors.with_opacity(0.25, T.SECONDARY_DARK),
                        offset=ft.Offset(0, 2),
                    ),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_SM,
        ),
        width=400,
        bgcolor=T.SURFACE,
        border_radius=T.RADIUS_LG,
        padding=ft.padding.all(T.SPACE_XL),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 4),
        ),
        border=ft.border.all(1, T.DIVIDER),
    )

    return ft.Container(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        t("pricing.title", lang),
                        size=T.FONT_H1,
                        weight=ft.FontWeight.BOLD,
                        color=T.TEXT_PRIMARY,
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
        bgcolor=T.BACKGROUND,
        alignment=ft.alignment.center,
    )


def _build_trust_badge(icon: str, label: str) -> ft.Control:
    """Build a single trust badge."""
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icon, color=T.TEXT_SECONDARY, size=18),
                ft.Text(
                    label,
                    size=T.FONT_CAPTION,
                    color=T.TEXT_SECONDARY,
                    weight=ft.FontWeight.W500,
                ),
            ],
            spacing=T.SPACE_SM,
        ),
        padding=ft.padding.symmetric(horizontal=T.SPACE_MD, vertical=T.SPACE_SM),
        border=ft.border.all(1, T.OUTLINE_VARIANT),
        border_radius=T.RADIUS_PILL,
        bgcolor=T.SURFACE,
    )


def _build_trust_bar(page: ft.Page) -> ft.Control:
    """Trust bar with security and compliance badges."""
    lang = page.session.store.get("lang") or "en"
    page_width = page.width or 800
    is_mobile = page_width < T.MOBILE_MAX

    badges = [
        _build_trust_badge(ft.Icons.FLAG, t("footer.made_in", lang) + " \U0001f1ea\U0001f1f8"),
        _build_trust_badge(ft.Icons.SHIELD, t("footer.gdpr", lang)),
        _build_trust_badge(ft.Icons.LOCK, "Stripe Secure"),
    ]

    if is_mobile:
        badges_layout = ft.Column(
            controls=badges,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=T.SPACE_SM,
        )
    else:
        badges_layout = ft.Row(
            controls=badges,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=T.SPACE_LG,
        )

    return ft.Container(
        content=ft.Container(
            content=badges_layout,
            width=T.MAX_WIDTH,
            padding=ft.padding.symmetric(
                horizontal=T.MOBILE_PADDING if is_mobile else T.CONTENT_PADDING,
                vertical=T.SPACE_XL,
            ),
        ),
        bgcolor=T.SURFACE,
        border=ft.border.symmetric(vertical=ft.BorderSide(1, T.DIVIDER)),
        alignment=ft.alignment.center,
    )


async def build(page: ft.Page) -> ft.View:
    """Build the landing page view."""
    lang = page.session.store.get("lang") or "en"
    return ft.View(
        route="/",
        controls=[
            build_navbar(page),
            _build_hero(page),
            _build_how_it_works(page),
            _build_style_showcase(page),
            _build_pricing(page),
            _build_trust_bar(page),
            build_footer(page),
            build_cookie_banner(page, lang),
        ],
        scroll=ft.ScrollMode.AUTO,
        padding=0,
        bgcolor=T.BACKGROUND,
    )
