"""Unit tests for app.theme — design-system constants validation."""

import re

from app.theme import StudioFaceTheme as T

# Regex for valid #RRGGBB hex color
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")

# All six expected headshot styles
ALL_STYLES = {"corporate", "medical", "banking", "startup", "casual", "tech"}


class TestColors:
    """Color constants must be valid hex."""

    # Collect all class-level color attributes that look like hex strings
    COLOR_ATTRS = [
        attr
        for attr in dir(T)
        if not attr.startswith("_")
        and isinstance(getattr(T, attr), str)
        and getattr(T, attr).startswith("#")
    ]

    def test_colors_are_valid_hex(self) -> None:
        assert len(self.COLOR_ATTRS) > 0, "No color constants found"
        for attr in self.COLOR_ATTRS:
            value = getattr(T, attr)
            assert HEX_RE.match(value), (
                f"{attr} = '{value}' is not valid #RRGGBB"
            )


class TestSpacing:
    """All SPACE_* values must sit on a 4px grid."""

    SPACE_ATTRS = [
        attr for attr in dir(T) if attr.startswith("SPACE_")
    ]

    def test_spacing_divisible_by_4(self) -> None:
        assert len(self.SPACE_ATTRS) > 0, "No SPACE_* constants found"
        for attr in self.SPACE_ATTRS:
            value = getattr(T, attr)
            assert isinstance(value, int), f"{attr} is not int"
            assert value % 4 == 0, f"{attr} = {value} is not divisible by 4"


class TestFontSizes:
    """FONT_* sizes must be reasonable and even."""

    FONT_ATTRS = [
        attr for attr in dir(T) if attr.startswith("FONT_") and isinstance(getattr(T, attr), int)
    ]

    def test_font_sizes_reasonable(self) -> None:
        assert len(self.FONT_ATTRS) > 0, "No FONT_* constants found"
        for attr in self.FONT_ATTRS:
            value = getattr(T, attr)
            assert 10 <= value <= 72, f"{attr} = {value} outside 10..72"

    def test_font_sizes_even(self) -> None:
        for attr in self.FONT_ATTRS:
            value = getattr(T, attr)
            assert value % 2 == 0, f"{attr} = {value} is not even"


class TestRadius:
    """RADIUS_* values must be positive."""

    RADIUS_ATTRS = [
        attr for attr in dir(T) if attr.startswith("RADIUS_")
    ]

    def test_radius_values_positive(self) -> None:
        assert len(self.RADIUS_ATTRS) > 0, "No RADIUS_* constants found"
        for attr in self.RADIUS_ATTRS:
            value = getattr(T, attr)
            assert isinstance(value, int), f"{attr} is not int"
            assert value > 0, f"{attr} = {value} is not positive"


class TestLayout:
    """Layout constants sanity checks."""

    def test_max_width_reasonable(self) -> None:
        assert 800 <= T.MAX_WIDTH <= 2000, (
            f"MAX_WIDTH = {T.MAX_WIDTH} outside 800..2000"
        )

    def test_breakpoints_ordered(self) -> None:
        assert T.MOBILE_MAX < T.TABLET_MAX, (
            f"MOBILE_MAX ({T.MOBILE_MAX}) >= TABLET_MAX ({T.TABLET_MAX})"
        )


class TestStyleMaps:
    """STYLE_COLORS and STYLE_ICONS must cover all 6 styles."""

    def test_style_colors_all_present(self) -> None:
        assert set(T.STYLE_COLORS.keys()) == ALL_STYLES, (
            f"STYLE_COLORS keys: {set(T.STYLE_COLORS.keys())} != {ALL_STYLES}"
        )

    def test_style_icons_all_present(self) -> None:
        assert set(T.STYLE_ICONS.keys()) == ALL_STYLES, (
            f"STYLE_ICONS keys: {set(T.STYLE_ICONS.keys())} != {ALL_STYLES}"
        )

    def test_style_colors_valid_hex(self) -> None:
        for style, color in T.STYLE_COLORS.items():
            assert HEX_RE.match(color), (
                f"STYLE_COLORS['{style}'] = '{color}' is not valid #RRGGBB"
            )
