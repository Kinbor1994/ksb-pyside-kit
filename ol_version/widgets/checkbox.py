from typing import Optional, Dict, Callable, Any
from ..core.commons import QCheckBox, QHBoxLayout
from ..core.base_form_field import BaseFormField
from ..core.themes.themes import ThemeManager, CheckboxTheme

class Checkbox(BaseFormField):
    """
    Checkbox form field component.
    
    Args:
        key (str, optional): Unique identifier
        width (int, optional): Width in pixels
        height (int, optional): Height in pixels
        tooltip (str, optional): Hover tooltip text
        visible (bool): Initial visibility state
        disabled (bool): Initial disabled state
        theme (CheckboxTheme): Theme configuration
        label (str, optional): Label text
        helper_text (str, optional): Helper text below field
        error_messages (Dict[str, str], optional): Custom error messages
        required (bool): Whether field is required
        value (bool, optional): Initial checked state
        tristate (bool): Allow indeterminate state
        on_change (Callable, optional): State change callback
        on_focus (Callable, optional): Focus callback
        on_blur (Callable, optional): Blur callback
        parent: Parent widget
    """
    
    def __init__(
        self,
        key: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        tooltip: Optional[str] = None,
        visible: bool = True,
        disabled: bool = False,
        theme: CheckboxTheme = ThemeManager.CheckboxThemes.DEFAULT,
        label: Optional[str] = None,
        helper_text: Optional[str] = None,
        error_messages: Optional[Dict[str, str]] = None,
        required: bool = False,
        value: bool = False,
        tristate: bool = False,
        on_change: Optional[Callable] = None,
        on_focus: Optional[Callable] = None,
        on_blur: Optional[Callable] = None,
        parent = None,
    ) -> None:
        self._initial_value = value
        self._tristate = tristate
        
        super().__init__(
            key=key,
            width=width,
            height=height,
            tooltip=tooltip,
            visible=visible,
            disabled=disabled,
            theme=theme,
            label=label,
            helper_text=helper_text,
            error_messages=error_messages or {"required": "Ce champ est requis"},
            required=required,
            on_change=on_change,
            on_focus=on_focus,
            on_blur=on_blur,
            parent=parent
        )

    def _create_form_field(self) -> None:
        """Create and configure the QCheckBox widget."""
        self.checkbox_layout = QHBoxLayout()
        self.checkbox_layout.setSpacing(5)
        self.checkbox_layout.setContentsMargins(0, 0, 0, 0)

        # Create checkbox
        self.checkbox = QCheckBox("", self)
        self._form_field_widget = self.checkbox
        
        # Configure tristate
        if self._tristate:
            self.checkbox.setTristate(True)
            
        # Configure dimensions
        if self._width and self._height:
            self.checkbox.setFixedSize(self._width, self._height)
        elif self._height:
            self.checkbox.setFixedHeight(self._height)
            
        # Set initial value
        if self._initial_value:
            self.set_value(self._initial_value)

        # Connect signals
        self.checkbox.stateChanged.connect(self._handle_state_changed)
        self._form_field_widget.installEventFilter(self)

        # Add to layout
        self.checkbox_layout.addWidget(self.checkbox)
        self.checkbox_layout.addStretch(1)
        self.main_layout.addLayout(self.checkbox_layout)

    def _handle_state_changed(self, state: int) -> None:
        """Handle checkbox state change events."""
        if self._on_change:
            self._on_change(self.get_value())
        self.is_valid()

    def is_valid(self) -> bool:
        """Validate the checkbox state."""
        if self._required and not self.get_value():
            self.show_error(self._error_messages["required"])
            return False
            
        self.hide_error()
        return True

    def get_value(self) -> Any:
        """Get current checkbox state."""
        if self._tristate:
            state = self.checkbox.checkState()
            return {
                0: False,    # Unchecked
                1: None,     # Partially checked
                2: True      # Checked
            }.get(state)
        return self.checkbox.isChecked()

    def set_value(self, value: Any) -> None:
        """Set checkbox state."""
        if self._tristate and value is None:
            self.checkbox.setCheckState(1)  # Partially checked
        else:
            self.checkbox.setChecked(bool(value))

    def clear_content(self) -> None:
        """Clear checkbox state."""
        super().clear_content()
        self.checkbox.setChecked(False)