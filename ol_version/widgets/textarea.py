from typing import Optional, Dict, Callable
from ..core.commons import QTextEdit, QHBoxLayout
from ..core.base_form_field import BaseFormField
from ..core.themes.themes import ThemeManager, TextAreaTheme

class TextArea(BaseFormField):
    """
    Multi-line text input field component.
    
    Args:
        key (str, optional): Unique identifier
        width (int, optional): Width in pixels
        height (int, optional): Height in pixels
        tooltip (str, optional): Hover tooltip text
        visible (bool): Initial visibility state
        disabled (bool): Initial disabled state
        theme (TextAreaTheme): Theme configuration
        label (str, optional): Label text
        hint_text (str, optional): Placeholder text
        helper_text (str, optional): Helper text below field
        error_messages (Dict[str, str], optional): Custom error messages
        required (bool): Whether field is required
        max_length (int, optional): Maximum text length
        min_length (int, optional): Minimum text length
        value (str, optional): Initial text value
        read_only (bool): Whether text is editable
        on_change (Callable, optional): Text change callback
        on_focus (Callable, optional): Focus callback
        on_blur (Callable, optional): Blur callback
        parent: Parent widget
    """
    
    def __init__(
        self,
        key: Optional[str] = None,
        width: Optional[int] = 300,
        height: Optional[int] = 100,  # Plus haut par défaut
        tooltip: Optional[str] = None,
        visible: bool = True,
        disabled: bool = False,
        theme: TextAreaTheme = ThemeManager.TextAreaThemes.DEFAULT,
        label: Optional[str] = None,
        hint_text: Optional[str] = None,
        helper_text: Optional[str] = None,
        error_messages: Optional[Dict[str, str]] = None,
        required: bool = False,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None,
        value: Optional[str] = None,
        read_only: bool = False,
        on_change: Optional[Callable] = None,
        on_focus: Optional[Callable] = None,
        on_blur: Optional[Callable] = None,
        parent = None,
    ) -> None:
        self._initial_value = value
        self._max_length = max_length
        self._min_length = min_length
        self._read_only = read_only
        
        # Initialize base form field
        super().__init__(
            key=key,
            width=width,
            height=height,
            tooltip=tooltip,
            visible=visible,
            disabled=disabled,
            theme=theme,
            label=label,
            hint_text=hint_text,
            helper_text=helper_text,
            error_messages=error_messages or {"required": "Ce champ est requis"},
            required=required,
            on_change=on_change,
            on_focus=on_focus,
            on_blur=on_blur,
            parent=parent
        )

    def _create_form_field(self) -> None:
        """Create and configure the QTextEdit widget."""
        self.textarea_layout = QHBoxLayout()
        self.textarea_layout.setSpacing(5)
        self.textarea_layout.setContentsMargins(0, 0, 0, 0)

        # Create text edit
        self.text_edit = QTextEdit(self)
        self._form_field_widget = self.text_edit
        
        # Configure dimensions
        if self._width and self._height:
            self.text_edit.setFixedSize(self._width, self._height)
        elif self._height:
            self.text_edit.setFixedHeight(self._height)
            
        # Set placeholder text
        if self._hint_text:
            self.text_edit.setPlaceholderText(self._hint_text)
            
        # Set initial value
        if self._initial_value:
            self.set_value(self._initial_value)
            
        # Configure read-only state
        self.text_edit.setReadOnly(self._read_only)
        
        # Connect signals
        self.text_edit.textChanged.connect(self._handle_text_changed)
        self._form_field_widget.installEventFilter(self)

        # Add to layout
        self.textarea_layout.addWidget(self.text_edit)
        self.textarea_layout.addStretch(1)
        self.main_layout.addLayout(self.textarea_layout)

    def _handle_text_changed(self) -> None:
        """Handle text change events."""
        if self._on_change:
            self._on_change(self.get_value())
        self.is_valid()

    def is_valid(self) -> bool:
        """Validate the text content."""
        value = self.get_value()
        
        if self._required and not value:
            self.show_error(self._error_messages["required"])
            return False
            
        if self._min_length and len(value) < self._min_length:
            self.show_error(f"Le texte doit contenir au moins {self._min_length} caractères")
            return False
            
        if self._max_length and len(value) > self._max_length:
            self.show_error(f"Le texte ne doit pas dépasser {self._max_length} caractères")
            return False
            
        self.hide_error()
        return True

    def get_value(self) -> str:
        """Get current text content."""
        return self.text_edit.toPlainText()

    def set_value(self, value: Optional[str]) -> None:
        """Set text content."""
        self.text_edit.setPlainText(value or "")

    def clear_content(self) -> None:
        """Clear text content."""
        super().clear_content()
        self.text_edit.clear()