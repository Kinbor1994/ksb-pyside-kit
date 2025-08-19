"""
Core Pydantic models for KSB PySide Kit.
Provides strongly typed configuration and validation for all widgets.
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Union, List, Callable, TypeVar, Generic
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_extra_types.color import Color
from pathlib import Path


# =============================================================================
# Base Configuration Models
# =============================================================================


class AlignmentEnum(str, Enum):
    """Text and widget alignment options."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    JUSTIFY = "justify"


class SizeUnit(str, Enum):
    """Size unit types."""

    PX = "px"
    PERCENT = "%"
    EM = "em"
    REM = "rem"


class FontWeight(str, Enum):
    """Font weight options."""

    THIN = "100"
    LIGHT = "300"
    NORMAL = "400"
    MEDIUM = "500"
    BOLD = "700"
    BLACK = "900"


class InputType(str, Enum):
    """Input field types."""

    TEXT = "text"
    EMAIL = "email"
    PASSWORD = "password"
    NUMBER = "number"
    TEL = "tel"
    URL = "url"
    SEARCH = "search"


# =============================================================================
# Style System Models
# =============================================================================


class Size(BaseModel):
    """Represents size with unit."""

    value: Union[int, float]
    unit: SizeUnit = SizeUnit.PX

    def __str__(self) -> str:
        return f"{self.value}{self.unit.value}"

    @classmethod
    def px(cls, value: Union[int, float]) -> Size:
        return cls(value=value, unit=SizeUnit.PX)

    @classmethod
    def percent(cls, value: Union[int, float]) -> Size:
        return cls(value=value, unit=SizeUnit.PERCENT)


class Spacing(BaseModel):
    """Spacing configuration (margin/padding)."""

    top: Size = Size.px(0)
    right: Size = Size.px(0)
    bottom: Size = Size.px(0)
    left: Size = Size.px(0)

    @classmethod
    def all(cls, value: Union[int, float, Size]) -> Spacing:
        """Create uniform spacing."""
        size = Size.px(value) if isinstance(value, (int, float)) else value
        return cls(top=size, right=size, bottom=size, left=size)

    @classmethod
    def symmetric(
        cls,
        vertical: Union[int, float, Size] = 0,
        horizontal: Union[int, float, Size] = 0,
    ) -> Spacing:
        """Create symmetric spacing."""
        v_size = Size.px(vertical) if isinstance(vertical, (int, float)) else vertical
        h_size = (
            Size.px(horizontal) if isinstance(horizontal, (int, float)) else horizontal
        )
        return cls(top=v_size, bottom=v_size, left=h_size, right=h_size)


class Border(BaseModel):
    """Border configuration."""

    width: Size = Size.px(1)
    color: Color = Color("#cccccc")
    style: str = "solid"
    radius: Size = Size.px(0)

    def to_css(self) -> str:
        return f"{self.width} {self.style} {self.color}; border-radius: {self.radius};"


class Shadow(BaseModel):
    """Box shadow configuration."""

    x: Size = Size.px(0)
    y: Size = Size.px(2)
    blur: Size = Size.px(4)
    spread: Size = Size.px(0)
    color: Color = Color("rgba(0, 0, 0, 0.1)")
    inset: bool = False

    def to_css(self) -> str:
        inset_str = "inset " if self.inset else ""
        return f"{inset_str}{self.x} {self.y} {self.blur} {self.spread} {self.color}"


class Typography(BaseModel):
    """Typography configuration."""

    font_family: str = "Arial, sans-serif"
    font_size: Size = Size.px(14)
    font_weight: FontWeight = FontWeight.NORMAL
    line_height: float = 1.4
    letter_spacing: Size = Size.px(0)
    color: Color = Color("#333333")
    text_align: AlignmentEnum = AlignmentEnum.LEFT
    text_decoration: Optional[str] = None
    text_transform: Optional[str] = None

    def to_css(self) -> Dict[str, str]:
        css = {
            "font-family": self.font_family,
            "font-size": str(self.font_size),
            "font-weight": self.font_weight.value,
            "line-height": str(self.line_height),
            "letter-spacing": str(self.letter_spacing),
            "color": str(self.color),
            "text-align": self.text_align.value,
        }
        if self.text_decoration:
            css["text-decoration"] = self.text_decoration
        if self.text_transform:
            css["text-transform"] = self.text_transform
        return css


class StyleState(BaseModel):
    """Style configuration for different widget states."""

    background_color: Optional[Color] = None
    border: Optional[Border] = None
    shadow: Optional[Shadow] = None
    typography: Optional[Typography] = None
    opacity: float = Field(1.0, ge=0.0, le=1.0)
    transform: Optional[str] = None
    transition: Optional[str] = None

    def merge_with(self, other: StyleState) -> StyleState:
        """Merge with another style state, with other taking precedence."""
        return StyleState(
            background_color=other.background_color or self.background_color,
            border=other.border or self.border,
            shadow=other.shadow or self.shadow,
            typography=other.typography or self.typography,
            opacity=other.opacity if other.opacity != 1.0 else self.opacity,
            transform=other.transform or self.transform,
            transition=other.transition or self.transition,
        )


class WidgetStyle(BaseModel):
    """Complete widget style configuration."""

    normal: StyleState = Field(default_factory=StyleState)
    hover: Optional[StyleState] = None
    active: Optional[StyleState] = None
    focus: Optional[StyleState] = None
    disabled: Optional[StyleState] = None

    padding: Spacing = Field(default_factory=lambda: Spacing.all(8))
    margin: Spacing = Field(default_factory=Spacing)

    min_width: Optional[Size] = None
    min_height: Optional[Size] = None
    max_width: Optional[Size] = None
    max_height: Optional[Size] = None

    def get_state_style(self, state: str = "normal") -> StyleState:
        """Get style for specific state."""
        state_style = getattr(self, state, None) or self.normal
        return self.normal.merge_with(state_style) if state != "normal" else state_style

    def to_stylesheet(self, widget_class: str = "QWidget") -> str:
        """Generate Qt stylesheet from style configuration."""
        css_parts = []

        # Normal state
        normal_css = self._state_to_css(self.normal)
        if normal_css:
            css_parts.append(f"{widget_class} {{ {normal_css} }}")

        # Other states
        for state_name, qt_selector in [
            ("hover", ":hover"),
            ("focus", ":focus"),
            ("active", ":pressed"),
            ("disabled", ":disabled"),
        ]:
            state_style = getattr(self, state_name)
            if state_style:
                state_css = self._state_to_css(state_style)
                if state_css:
                    css_parts.append(f"{widget_class}{qt_selector} {{ {state_css} }}")

        return "\n".join(css_parts)

    def _state_to_css(self, state: StyleState) -> str:
        """Convert style state to CSS string."""
        css_parts = []

        if state.background_color:
            css_parts.append(f"background-color: {state.background_color};")

        if state.border:
            css_parts.append(f"border: {state.border.to_css()}")

        if state.shadow:
            css_parts.append(f"box-shadow: {state.shadow.to_css()};")

        if state.typography:
            for prop, value in state.typography.to_css().items():
                css_parts.append(f"{prop}: {value};")

        if state.opacity != 1.0:
            css_parts.append(f"opacity: {state.opacity};")

        if state.transform:
            css_parts.append(f"transform: {state.transform};")

        if state.transition:
            css_parts.append(f"transition: {state.transition};")

        # Add padding and margin
        css_parts.append(
            f"padding: {self.padding.top} {self.padding.right} {self.padding.bottom} {self.padding.left};"
        )
        css_parts.append(
            f"margin: {self.margin.top} {self.margin.right} {self.margin.bottom} {self.margin.left};"
        )

        return " ".join(css_parts)


# =============================================================================
# Widget Configuration Models
# =============================================================================


class BaseWidgetConfig(BaseModel):
    """Base configuration for all widgets."""

    key: Optional[str] = None
    width: Optional[Size] = None
    height: Optional[Size] = None
    tooltip: Optional[str] = None
    visible: bool = True
    disabled: bool = False
    style: WidgetStyle = Field(default_factory=WidgetStyle)

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True


class FormFieldConfig(BaseWidgetConfig):
    """Base configuration for form fields."""

    label: Optional[str] = None
    help_text: Optional[str] = None
    placeholder: Optional[str] = None
    required: bool = False
    read_only: bool = False
    auto_focus: bool = False

    # Validation
    validators: List[Callable[[Any], bool]] = Field(default_factory=list)
    error_messages: Dict[str, str] = Field(default_factory=dict)

    # Events
    on_change: Optional[Callable[[Any], None]] = None
    on_focus: Optional[Callable[[], None]] = None
    on_blur: Optional[Callable[[], None]] = None
    on_validate: Optional[Callable[[Any], bool]] = None

    @field_validator("error_messages", always=True)
    def set_default_error_messages(cls, v):
        default_messages = {
            "required": "Ce champ est requis.",
            "invalid": "Valeur invalide.",
        }
        default_messages.update(v)
        return default_messages


class TextFieldConfig(FormFieldConfig):
    """Configuration for text input fields."""

    input_type: InputType = InputType.TEXT
    min_length: Optional[int] = Field(None, ge=0)
    max_length: Optional[int] = Field(None, ge=1)
    pattern: Optional[str] = None
    autocomplete: bool = True
    spellcheck: bool = True

    # Password specific
    show_password_toggle: bool = False

    # Number specific
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None

    @model_validator
    def validate_constraints(cls, values):
        """Validate field constraints."""
        min_len = values.get("min_length")
        max_len = values.get("max_length")

        if min_len is not None and max_len is not None and min_len > max_len:
            raise ValueError("min_length cannot be greater than max_length")

        min_val = values.get("min_value")
        max_val = values.get("max_value")

        if min_val is not None and max_val is not None and min_val > max_val:
            raise ValueError("min_value cannot be greater than max_value")

        return values


class ButtonConfig(BaseWidgetConfig):
    """Configuration for button widgets."""

    text: str = ""
    icon: Optional[str] = None
    icon_size: Size = Size.px(16)
    icon_position: AlignmentEnum = AlignmentEnum.LEFT

    # Button specific
    checkable: bool = False
    checked: bool = False
    default: bool = False
    flat: bool = False

    # Events
    on_click: Optional[Callable[[], None]] = None
    on_toggle: Optional[Callable[[bool], None]] = None


class ComboBoxConfig(FormFieldConfig):
    """Configuration for combo box widgets."""

    options: List[Union[str, Dict[str, Any]]] = Field(default_factory=list)
    searchable: bool = True
    multiple: bool = False
    clear_button: bool = True

    @field_validator("options")
    def validate_options(cls, v):
        """Validate options format."""
        for option in v:
            if isinstance(option, dict) and "value" not in option:
                raise ValueError("Dict options must have a 'value' key")
        return v


# =============================================================================
# Theme System Models
# =============================================================================


class ThemeConfig(BaseModel):
    """Theme configuration."""

    name: str
    description: Optional[str] = None

    # Color palette
    primary_color: Color = Color("#007bff")
    secondary_color: Color = Color("#6c757d")
    success_color: Color = Color("#28a745")
    warning_color: Color = Color("#ffc107")
    error_color: Color = Color("#dc3545")
    info_color: Color = Color("#17a2b8")

    # Neutral colors
    background_color: Color = Color("#ffffff")
    surface_color: Color = Color("#f8f9fa")
    text_color: Color = Color("#212529")
    text_muted_color: Color = Color("#6c757d")
    border_color: Color = Color("#dee2e6")

    # Typography
    font_family_primary: str = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    font_family_monospace: str = "SF Mono, Monaco, Consolas, monospace"

    font_size_xs: Size = Size.px(12)
    font_size_sm: Size = Size.px(14)
    font_size_md: Size = Size.px(16)
    font_size_lg: Size = Size.px(18)
    font_size_xl: Size = Size.px(20)
    font_size_xxl: Size = Size.px(24)

    # Spacing scale
    spacing_xs: Size = Size.px(4)
    spacing_sm: Size = Size.px(8)
    spacing_md: Size = Size.px(16)
    spacing_lg: Size = Size.px(24)
    spacing_xl: Size = Size.px(32)
    spacing_xxl: Size = Size.px(48)

    # Border radius
    border_radius_sm: Size = Size.px(4)
    border_radius_md: Size = Size.px(8)
    border_radius_lg: Size = Size.px(12)
    border_radius_xl: Size = Size.px(16)

    # Shadows
    shadow_sm: Shadow = Field(
        default_factory=lambda: Shadow(
            y=Size.px(1), blur=Size.px(3), color=Color("rgba(0, 0, 0, 0.1)")
        )
    )
    shadow_md: Shadow = Field(
        default_factory=lambda: Shadow(
            y=Size.px(4), blur=Size.px(6), color=Color("rgba(0, 0, 0, 0.1)")
        )
    )
    shadow_lg: Shadow = Field(
        default_factory=lambda: Shadow(
            y=Size.px(10), blur=Size.px(15), color=Color("rgba(0, 0, 0, 0.1)")
        )
    )

    def get_widget_style(
        self, widget_type: str, variant: str = "default"
    ) -> WidgetStyle:
        """Get predefined style for widget type and variant."""
        if widget_type == "button":
            return self._get_button_style(variant)
        elif widget_type == "text_field":
            return self._get_text_field_style(variant)
        elif widget_type == "text":
            return self._get_text_style(variant)
        else:
            return WidgetStyle()

    def _get_button_style(self, variant: str = "primary") -> WidgetStyle:
        """Get button style based on variant."""
        color_map = {
            "primary": self.primary_color,
            "secondary": self.secondary_color,
            "success": self.success_color,
            "warning": self.warning_color,
            "error": self.error_color,
        }

        bg_color = color_map.get(variant, self.primary_color)

        return WidgetStyle(
            normal=StyleState(
                background_color=bg_color,
                border=Border(
                    width=Size.px(1), color=bg_color, radius=self.border_radius_md
                ),
                typography=Typography(
                    color=Color("#ffffff"),
                    font_weight=FontWeight.MEDIUM,
                    text_align=AlignmentEnum.CENTER,
                ),
            ),
            hover=StyleState(
                background_color=Color(f"rgba({bg_color.as_rgb()}, 0.9)"),
                transform="translateY(-1px)",
                shadow=self.shadow_md,
            ),
            active=StyleState(
                background_color=Color(f"rgba({bg_color.as_rgb()}, 0.8)"),
                transform="translateY(0px)",
            ),
            padding=Spacing.symmetric(vertical=12, horizontal=24),
        )

    def _get_text_field_style(self, variant: str = "default") -> WidgetStyle:
        """Get text field style."""
        return WidgetStyle(
            normal=StyleState(
                background_color=self.background_color,
                border=Border(
                    width=Size.px(1),
                    color=self.border_color,
                    radius=self.border_radius_md,
                ),
                typography=Typography(
                    font_family=self.font_family_primary,
                    font_size=self.font_size_md,
                    color=self.text_color,
                ),
            ),
            focus=StyleState(
                border=Border(
                    width=Size.px(2),
                    color=self.primary_color,
                    radius=self.border_radius_md,
                ),
                shadow=Shadow(
                    y=Size.px(0),
                    blur=Size.px(0),
                    spread=Size.px(3),
                    color=Color(f"rgba({self.primary_color.as_rgb()}, 0.1)"),
                ),
            ),
            padding=Spacing.symmetric(vertical=10, horizontal=12),
        )

    def _get_text_style(self, variant: str = "body") -> WidgetStyle:
        """Get text style based on variant."""
        size_map = {
            "heading": self.font_size_xl,
            "subheading": self.font_size_lg,
            "body": self.font_size_md,
            "caption": self.font_size_sm,
            "overline": self.font_size_xs,
        }

        weight_map = {
            "heading": FontWeight.BOLD,
            "subheading": FontWeight.MEDIUM,
            "body": FontWeight.NORMAL,
            "caption": FontWeight.NORMAL,
            "overline": FontWeight.MEDIUM,
        }

        return WidgetStyle(
            normal=StyleState(
                typography=Typography(
                    font_family=self.font_family_primary,
                    font_size=size_map.get(variant, self.font_size_md),
                    font_weight=weight_map.get(variant, FontWeight.NORMAL),
                    color=self.text_color,
                )
            )
        )


# =============================================================================
# Predefined Themes
# =============================================================================


class Themes:
    """Collection of predefined themes."""

    @staticmethod
    def light() -> ThemeConfig:
        """Light theme configuration."""
        return ThemeConfig(
            name="light", description="Clean light theme with modern aesthetics"
        )

    @staticmethod
    def dark() -> ThemeConfig:
        """Dark theme configuration."""
        return ThemeConfig(
            name="dark",
            description="Modern dark theme",
            background_color=Color("#1a1a1a"),
            surface_color=Color("#2d2d2d"),
            text_color=Color("#ffffff"),
            text_muted_color=Color("#a0a0a0"),
            border_color=Color("#404040"),
        )

    @staticmethod
    def material() -> ThemeConfig:
        """Material Design inspired theme."""
        return ThemeConfig(
            name="material",
            description="Material Design inspired theme",
            primary_color=Color("#1976d2"),
            secondary_color=Color("#dc004e"),
            border_radius_md=Size.px(4),
            shadow_md=Shadow(
                y=Size.px(2),
                blur=Size.px(4),
                spread=Size.px(1),
                color=Color("rgba(0, 0, 0, 0.2)"),
            ),
        )
