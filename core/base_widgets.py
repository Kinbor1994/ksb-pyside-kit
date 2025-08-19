"""
Base widgets.
"""

from __future__ import annotations
from typing import Any, Optional, Dict, List, Type, TypeVar, Generic, Union
from abc import ABC, abstractmethod
import logging
from contextlib import contextmanager

from .qt_imports import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QObject,
    QEvent,
    Signal,
    QTimer,
    QFont,
)

from pydantic import ValidationError

from .models import BaseWidgetConfig, FormFieldConfig, ThemeConfig, WidgetStyle, Themes

# Type variables for generic typing
ConfigType = TypeVar("ConfigType", bound=BaseWidgetConfig)
WidgetType = TypeVar("WidgetType", bound=QWidget)

logger = logging.getLogger(__name__)


# =============================================================================
# Base Widget Classes
# =============================================================================


class BaseWidget(QWidget, Generic[ConfigType]):
    """
    Enhanced base widget with Pydantic configuration and modern theming.

    Features:
    - Type-safe configuration with Pydantic
    - Flexible styling system
    - Event handling with validation
    - Automatic error handling and logging
    - Theme inheritance and customization

    Type Parameters:
        ConfigType: The Pydantic model type for widget configuration
    """

    # Signals
    config_changed = Signal(object)  # Emitted when configuration changes
    style_changed = Signal(object)  # Emitted when style changes
    validation_error = Signal(str)  # Emitted on validation errors

    def __init__(
        self,
        config: Optional[ConfigType] = None,
        theme: Optional[ThemeConfig] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the base widget.

        Args:
            config: Widget configuration (Pydantic model)
            theme: Theme configuration
            parent: Parent widget
        """
        super().__init__(parent)

        # Configuration
        self._config: ConfigType = config or self._get_default_config()
        self._theme: ThemeConfig = theme or Themes.light()
        self._validation_errors: List[str] = []

        # Internal state
        self._is_initializing = True
        self._style_cache: Dict[str, str] = {}

        # Setup widget
        self._setup_widget()
        self._setup_layout()
        self._setup_styling()
        self._setup_events()
        self._is_initializing = False

        # Apply initial configuration
        self.apply_config(self._config)

    @abstractmethod
    def _get_default_config(self) -> ConfigType:
        """Get default configuration for this widget type."""
        pass

    def _setup_widget(self) -> None:
        """Setup basic widget properties."""
        if self._config.key:
            self.setObjectName(self._config.key)

        self.setVisible(self._config.visible)
        self.setEnabled(not self._config.disabled)

        if self._config.tooltip:
            self.setToolTip(self._config.tooltip)

    def _setup_layout(self) -> None:
        """Setup widget layout structure."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

    def _setup_styling(self) -> None:
        """Setup widget styling."""
        self._apply_style()

    def _setup_events(self) -> None:
        """Setup event connections."""
        self.config_changed.connect(self._on_config_changed)
        self.style_changed.connect(self._on_style_changed)

    def _apply_style(self) -> None:
        """Apply style configuration to widget."""
        try:
            stylesheet = self._config.style.to_stylesheet(self.__class__.__name__)
            if stylesheet != self._style_cache.get("current"):
                self.setStyleSheet(stylesheet)
                self._style_cache["current"] = stylesheet
                self.style_changed.emit(self._config.style)
        except Exception as e:
            logger.error(f"Error applying style to {self.__class__.__name__}: {e}")

    def apply_config(self, config: ConfigType) -> bool:
        """
        Apply new configuration to widget.

        Args:
            config: New configuration to apply

        Returns:
            bool: True if configuration was applied successfully
        """
        try:
            # Validate configuration
            if isinstance(config, dict):
                config = self._config.__class__(**config)

            old_config = self._config
            self._config = config

            # Apply configuration changes
            self._apply_config_changes(old_config, config)

            if not self._is_initializing:
                self.config_changed.emit(config)

            return True

        except ValidationError as e:
            error_msg = f"Configuration validation failed: {e}"
            self._validation_errors.append(error_msg)
            self.validation_error.emit(error_msg)
            logger.error(error_msg)
            return False
        except Exception as e:
            error_msg = f"Error applying configuration: {e}"
            logger.error(error_msg)
            return False

    def _apply_config_changes(
        self, old_config: ConfigType, new_config: ConfigType
    ) -> None:
        """Apply configuration changes to widget."""
        # Update basic properties
        if old_config.visible != new_config.visible:
            self.setVisible(new_config.visible)

        if old_config.disabled != new_config.disabled:
            self.setEnabled(not new_config.disabled)

        if old_config.tooltip != new_config.tooltip:
            self.setToolTip(new_config.tooltip or "")

        if old_config.style != new_config.style:
            self._apply_style()

    def update_style(self, **style_updates: Any) -> bool:
        """
        Update widget style with partial changes.

        Args:
            **style_updates: Style properties to update

        Returns:
            bool: True if style was updated successfully
        """
        try:
            # Create updated style configuration
            style_dict = self._config.style.dict()
            style_dict.update(style_updates)
            new_style = WidgetStyle(**style_dict)

            # Update configuration
            config_dict = self._config.dict()
            config_dict["style"] = new_style
            new_config = self._config.__class__(**config_dict)

            return self.apply_config(new_config)

        except Exception as e:
            logger.error(f"Error updating style: {e}")
            return False

    def set_theme(self, theme: ThemeConfig) -> None:
        """Set widget theme."""
        self._theme = theme
        # Apply theme-based styles
        widget_style = theme.get_widget_style(
            self.__class__.__name__.lower().replace("widget", "")
        )
        self.update_style(**widget_style.dict())

    def _on_config_changed(self, config: ConfigType) -> None:
        """Handle configuration change events."""
        pass

    def _on_style_changed(self, style: WidgetStyle) -> None:
        """Handle style change events."""
        pass

    @property
    def config(self) -> ConfigType:
        """Get current widget configuration."""
        return self._config

    @property
    def theme(self) -> ThemeConfig:
        """Get current widget theme."""
        return self._theme

    @property
    def validation_errors(self) -> List[str]:
        """Get current validation errors."""
        return self._validation_errors.copy()

    def clear_validation_errors(self) -> None:
        """Clear validation errors."""
        self._validation_errors.clear()


class FormFieldWidget(BaseWidget[FormFieldConfig], ABC):
    """
    Base class for form field widgets with validation and error handling.

    Features:
    - Built-in validation system
    - Error display management
    - Label and help text support
    - Value change tracking
    - Focus management
    """

    # Additional signals for form fields
    value_changed = Signal(object)  # Emitted when field value changes
    validation_state_changed = Signal(bool)  # Emitted when validation state changes
    focus_gained = Signal()  # Emitted when field gains focus
    focus_lost = Signal()  # Emitted when field loses focus

    def __init__(
        self,
        config: Optional[FormFieldConfig] = None,
        theme: Optional[ThemeConfig] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        # Form field state
        self._value: Any = None
        self._is_valid: bool = True
        self._error_message: Optional[str] = None
        self._has_been_touched: bool = False

        # UI components
        self._label_widget: Optional[QLabel] = None
        self._error_widget: Optional[QLabel] = None
        self._help_widget: Optional[QLabel] = None
        self._field_widget: Optional[QWidget] = None

        super().__init__(config, theme, parent)

        # Connect form field events
        self.value_changed.connect(self._on_value_changed)
        self.validation_state_changed.connect(self._on_validation_state_changed)

    def _get_default_config(self) -> FormFieldConfig:
        """Get default form field configuration."""
        return FormFieldConfig()

    def _setup_layout(self) -> None:
        """Setup form field layout structure."""
        super()._setup_layout()

        # Create label if specified
        if self._config.label:
            self._create_label()

        # Create main field widget
        self._create_field_widget()

        # Create help text if specified
        if self._config.help_text:
            self._create_help_text()

        # Create error display (hidden by default)
        self._create_error_display()

    def _create_label(self) -> None:
        """Create and setup field label."""
        self._label_widget = QLabel(self._config.label)
        self._label_widget.setObjectName(f"{self.objectName()}_label")

        # Apply label styling from theme
        label_style = self._theme.get_widget_style("text", "caption")
        self._label_widget.setStyleSheet(label_style.to_stylesheet("QLabel"))

        # Add required indicator
        if self._config.required:
            self._label_widget.setText(f"{self._config.label} *")

        self.main_layout.addWidget(self._label_widget)

    @abstractmethod
    def _create_field_widget(self) -> None:
        """Create the main field widget. Must be implemented by subclasses."""
        pass

    def _create_help_text(self) -> None:
        """Create and setup help text."""
        self._help_widget = QLabel(self._config.help_text)
        self._help_widget.setObjectName(f"{self.objectName()}_help")
        self._help_widget.setWordWrap(True)

        # Apply help text styling
        help_style = self._theme.get_widget_style("text", "caption")
        help_style.normal.typography.color = self._theme.text_muted_color
        self._help_widget.setStyleSheet(help_style.to_stylesheet("QLabel"))

        self.main_layout.addWidget(self._help_widget)

    def _create_error_display(self) -> None:
        """Create and setup error message display."""
        self._error_widget = QLabel()
        self._error_widget.setObjectName(f"{self.objectName()}_error")
        self._error_widget.setWordWrap(True)
        self._error_widget.setVisible(False)

        # Apply error styling
        error_style = self._theme.get_widget_style("text", "caption")
        error_style.normal.typography.color = self._theme.error_color
        self._error_widget.setStyleSheet(error_style.to_stylesheet("QLabel"))

        self.main_layout.addWidget(self._error_widget)

    def _apply_config_changes(
        self, old_config: FormFieldConfig, new_config: FormFieldConfig
    ) -> None:
        """Apply form field configuration changes."""
        super()._apply_config_changes(old_config, new_config)

        # Update label
        if old_config.label != new_config.label:
            if new_config.label and not self._label_widget:
                self._create_label()
            elif self._label_widget:
                label_text = new_config.label or ""
                if new_config.required:
                    label_text += " *"
                self._label_widget.setText(label_text)

        # Update help text
        if old_config.help_text != new_config.help_text:
            if new_config.help_text and not self._help_widget:
                self._create_help_text()
            elif self._help_widget:
                self._help_widget.setText(new_config.help_text or "")
                self._help_widget.setVisible(bool(new_config.help_text))

        # Update read-only state
        if old_config.read_only != new_config.read_only and self._field_widget:
            self._set_read_only(new_config.read_only)

    @abstractmethod
    def _set_read_only(self, read_only: bool) -> None:
        """Set read-only state for the field widget."""
        pass

    @abstractmethod
    def get_value(self) -> Any:
        """Get current field value."""
        pass

    @abstractmethod
    def set_value(self, value: Any) -> bool:
        """Set field value."""
        pass

    def validate(self) -> bool:
        """
        Validate current field value.

        Returns:
            bool: True if field is valid, False otherwise
        """
        try:
            value = self.get_value()
            errors = []

            # Required field validation
            if self._config.required and (value is None or value == ""):
                errors.append(
                    self._config.error_messages.get("required", "Ce champ est requis.")
                )

            # Run custom validators
            for validator in self._config.validators:
                try:
                    if not validator(value):
                        errors.append(
                            self._config.error_messages.get(
                                "invalid", "Valeur invalide."
                            )
                        )
                except Exception as e:
                    errors.append(f"Erreur de validation: {str(e)}")

            # Run custom validation hook
            if self._config.on_validate:
                try:
                    if not self._config.on_validate(value):
                        errors.append(
                            self._config.error_messages.get(
                                "invalid", "Valeur invalide."
                            )
                        )
                except Exception as e:
                    errors.append(f"Erreur de validation: {str(e)}")

            # Update validation state
            is_valid = len(errors) == 0
            error_message = "; ".join(errors) if errors else None

            self._set_validation_state(is_valid, error_message)

            return is_valid

        except Exception as e:
            error_msg = f"Erreur lors de la validation: {str(e)}"
            logger.error(error_msg)
            self._set_validation_state(False, error_msg)
            return False

    def _set_validation_state(
        self, is_valid: bool, error_message: Optional[str] = None
    ) -> None:
        """Set validation state and update UI."""
        old_valid = self._is_valid
        self._is_valid = is_valid
        self._error_message = error_message

        # Update error display
        if self._error_widget:
            if error_message and not is_valid:
                self._error_widget.setText(error_message)
                self._error_widget.setVisible(True)
            else:
                self._error_widget.setVisible(False)

        # Update field styling based on validation state
        self._update_validation_styling()

        # Emit signal if validation state changed
        if old_valid != is_valid:
            self.validation_state_changed.emit(is_valid)

    def _update_validation_styling(self) -> None:
        """Update field styling based on validation state."""
        if not self._field_widget:
            return

        if not self._is_valid:
            # Apply error styling
            error_style = self._theme.get_widget_style("text_field", "error")
            if not hasattr(self._theme, "_error_style_cache"):
                # Create error variant if not exists
                error_style.normal.border.color = self._theme.error_color
            self._field_widget.setStyleSheet(error_style.to_stylesheet())
        else:
            # Apply normal styling
            normal_style = self._config.style
            self._field_widget.setStyleSheet(normal_style.to_stylesheet())

    def clear_value(self) -> None:
        """Clear field value."""
        self.set_value(None)

    def reset(self) -> None:
        """Reset field to initial state."""
        self.clear_value()
        self._has_been_touched = False
        self._set_validation_state(True, None)

    def _on_value_changed(self, value: Any) -> None:
        """Handle value change events."""
        self._value = value
        self._has_been_touched = True

        # Trigger validation if field has been touched
        if self._has_been_touched:
            QTimer.singleShot(100, self.validate)  # Debounce validation

        # Call config callback
        if self._config.on_change:
            try:
                self._config.on_change(value)
            except Exception as e:
                logger.error(f"Error in on_change callback: {e}")

    def _on_validation_state_changed(self, is_valid: bool) -> None:
        """Handle validation state change events."""
        pass

    def _on_focus_gained(self) -> None:
        """Handle focus gained events."""
        if self._config.on_focus:
            try:
                self._config.on_focus()
            except Exception as e:
                logger.error(f"Error in on_focus callback: {e}")

        self.focus_gained.emit()

    def _on_focus_lost(self) -> None:
        """Handle focus lost events."""
        self._has_been_touched = True

        # Validate on blur
        self.validate()

        if self._config.on_blur:
            try:
                self._config.on_blur()
            except Exception as e:
                logger.error(f"Error in on_blur callback: {e}")

        self.focus_lost.emit()

    @property
    def is_valid(self) -> bool:
        """Check if field is currently valid."""
        return self._is_valid

    @property
    def error_message(self) -> Optional[str]:
        """Get current error message."""
        return self._error_message

    @property
    def has_been_touched(self) -> bool:
        """Check if field has been interacted with."""
        return self._has_been_touched


# =============================================================================
# Widget Factory System
# =============================================================================


class WidgetFactory:
    """
    Factory for creating widgets with type safety and configuration validation.
    """

    _widget_registry: Dict[str, Type[BaseWidget]] = {}

    @classmethod
    def register(cls, widget_type: str, widget_class: Type[BaseWidget]) -> None:
        """Register a widget class with the factory."""
        cls._widget_registry[widget_type] = widget_class

    @classmethod
    def create(
        cls,
        widget_type: str,
        config: Optional[Union[Dict[str, Any], BaseWidgetConfig]] = None,
        theme: Optional[ThemeConfig] = None,
        parent: Optional[QWidget] = None,
    ) -> BaseWidget:
        """
        Create a widget instance.

        Args:
            widget_type: Type of widget to create
            config: Widget configuration (dict or Pydantic model)
            theme: Theme configuration
            parent: Parent widget

        Returns:
            BaseWidget: Created widget instance

        Raises:
            ValueError: If widget type is not registered
            ValidationError: If configuration is invalid
        """
        if widget_type not in cls._widget_registry:
            raise ValueError(f"Unknown widget type: {widget_type}")

        widget_class = cls._widget_registry[widget_type]

        # Convert dict config to Pydantic model if needed
        if isinstance(config, dict):
            # Get the config class from widget class annotations
            config_class = widget_class.__orig_bases__[0].__args__[0]
            config = config_class(**config)

        return widget_class(config=config, theme=theme, parent=parent)


# =============================================================================
# Event System
# =============================================================================


class WidgetEventFilter(QObject):
    """Event filter for handling widget focus and interaction events."""

    focus_gained = Signal(QWidget)
    focus_lost = Signal(QWidget)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Filter events for focus tracking."""
        if isinstance(obj, QWidget):
            if event.type() == QEvent.FocusIn:
                self.focus_gained.emit(obj)
            elif event.type() == QEvent.FocusOut:
                self.focus_lost.emit(obj)

        return super().eventFilter(obj, event)


# =============================================================================
# Context Managers
# =============================================================================


@contextmanager
def widget_update_context(widget: BaseWidget):
    """Context manager for batch widget updates."""
    widget.setUpdatesEnabled(False)
    try:
        yield widget
    finally:
        widget.setUpdatesEnabled(True)
        widget.update()


@contextmanager
def theme_context(theme: ThemeConfig):
    """Context manager for applying theme to multiple widgets."""
    widgets = []

    def apply_theme(widget: BaseWidget):
        widgets.append(widget)
        widget.set_theme(theme)

    yield apply_theme

    # Additional cleanup if needed
    for widget in widgets:
        widget.update()


# =============================================================================
# Utilities
# =============================================================================


def create_separator(
    orientation: str = "horizontal", theme: Optional[ThemeConfig] = None
) -> QFrame:
    """
    Create a separator widget.

    Args:
        orientation: "horizontal" or "vertical"
        theme: Theme configuration

    Returns:
        QFrame: Configured separator
    """
    separator = QFrame()

    if orientation == "horizontal":
        separator.setFrameShape(QFrame.HLine)
    else:
        separator.setFrameShape(QFrame.VLine)

    separator.setFrameShadow(QFrame.Sunken)

    if theme:
        # Apply theme-based styling
        separator.setStyleSheet(
            f"""
            QFrame {{
                color: {theme.border_color};
                background-color: {theme.border_color};
            }}
        """
        )

    return separator


def apply_theme_to_widget_tree(widget: QWidget, theme: ThemeConfig) -> None:
    """
    Apply theme to a widget and all its children that are BaseWidget instances.

    Args:
        widget: Root widget
        theme: Theme to apply
    """
    if isinstance(widget, BaseWidget):
        widget.set_theme(theme)

    # Recursively apply to children
    for child in widget.findChildren(QWidget):
        if isinstance(child, BaseWidget):
            child.set_theme(theme)
