"""StudioFace Design System — Single source of truth for all visual design."""


class StudioFaceTheme:
    """Material Design 3 theme constants for StudioFace."""

    # Colors — Primary palette
    PRIMARY = "#1A237E"
    PRIMARY_LIGHT = "#534BAE"
    PRIMARY_DARK = "#000051"
    PRIMARY_CONTAINER = "#E8EAF6"

    # Colors — Secondary palette
    SECONDARY = "#FF6F00"
    SECONDARY_LIGHT = "#FFA040"
    SECONDARY_DARK = "#C43E00"
    SECONDARY_CONTAINER = "#FFF3E0"

    # Colors — Surface and background
    BACKGROUND = "#FAFAFA"
    SURFACE = "#FFFFFF"
    SURFACE_VARIANT = "#F5F5F5"
    ON_SURFACE = "#212121"

    # Colors — Semantic
    ERROR = "#D32F2F"
    ERROR_CONTAINER = "#FFEBEE"
    SUCCESS = "#388E3C"
    SUCCESS_CONTAINER = "#E8F5E9"
    WARNING = "#F57F17"
    WARNING_CONTAINER = "#FFFDE7"
    INFO = "#1565C0"
    INFO_CONTAINER = "#E3F2FD"

    # Colors — Text
    TEXT_PRIMARY = "#212121"
    TEXT_SECONDARY = "#757575"
    TEXT_DISABLED = "#BDBDBD"
    TEXT_ON_PRIMARY = "#FFFFFF"
    TEXT_ON_SECONDARY = "#FFFFFF"

    # Colors — Borders and dividers
    DIVIDER = "#E0E0E0"
    OUTLINE = "#BDBDBD"
    OUTLINE_VARIANT = "#E0E0E0"

    # Colors — Gradient pairs
    GRADIENT_START = "#1A237E"
    GRADIENT_END = "#534BAE"

    # Spacing — 4px grid system
    SPACE_XS = 4
    SPACE_SM = 8
    SPACE_MD = 16
    SPACE_LG = 24
    SPACE_XL = 32
    SPACE_XXL = 48
    SPACE_HERO = 64

    # Border radius
    RADIUS_SM = 8
    RADIUS_MD = 12
    RADIUS_LG = 24
    RADIUS_PILL = 100

    # Typography — font sizes
    FONT_HERO = 48
    FONT_H1 = 36
    FONT_H2 = 28
    FONT_H3 = 22
    FONT_H4 = 18
    FONT_BODY = 16
    FONT_CAPTION = 14
    FONT_SMALL = 12

    # Typography — font weights (string values for Flet)
    WEIGHT_LIGHT = "w300"
    WEIGHT_REGULAR = "w400"
    WEIGHT_MEDIUM = "w500"
    WEIGHT_SEMIBOLD = "w600"
    WEIGHT_BOLD = "w700"

    # Layout
    MAX_WIDTH = 1200
    CONTENT_PADDING = 24
    MOBILE_PADDING = 16
    CARD_ELEVATION = 2
    CARD_PADDING = 24

    # Breakpoints
    MOBILE_MAX = 600
    TABLET_MAX = 1024

    # Animation durations (ms)
    ANIM_FAST = 150
    ANIM_NORMAL = 300
    ANIM_SLOW = 500

    # Style card colors — one per headshot style
    STYLE_COLORS = {
        "corporate": "#1A237E",
        "medical": "#1565C0",
        "banking": "#283593",
        "startup": "#FF6F00",
        "casual": "#388E3C",
        "tech": "#6A1B9A",
    }

    # Style icons — Flet icon names
    STYLE_ICONS = {
        "corporate": "business_center",
        "medical": "local_hospital",
        "banking": "account_balance",
        "startup": "rocket_launch",
        "casual": "emoji_people",
        "tech": "computer",
    }
