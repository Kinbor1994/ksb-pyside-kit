from typing import Optional, Dict, Callable, Any, List
from ..core.commons import QComboBox, QHBoxLayout, Qt, QStringListModel, QCompleter
from ..core.base_form_field import BaseFormField
from ..core.themes.themes import ThemeManager, ComboBoxTheme

class ComboBox(BaseFormField):
    """
    A form field widget for ComboBox with integrated search functionality.

    Args:
        key (str, optional): Unique identifier
        width (int, optional): Width in pixels
        height (int, optional): Height in pixels
        tooltip (str, optional): Hover tooltip text
        visible (bool): Initial visibility state
        disabled (bool): Initial disabled state
        theme (ComboBoxTheme): Theme configuration
        label (str, optional): Label text
        hint_text (str, optional): Placeholder text
        helper_text (str, optional): Helper text
        error_messages (Dict[str, str], optional): Custom error messages
        required (bool): Whether selection is required
        options (List): Available options
        value (Any, optional): Initial value
        on_change (Callable, optional): Selection change callback
        on_focus (Callable, optional): Focus callback
        on_blur (Callable, optional): Blur callback
        parent (QWidget, optional): Parent widget
    """

    def __init__(
        self,
        key: Optional[str] = None,
        width: Optional[int] = 300,
        height: Optional[int] = 40,
        tooltip: Optional[str] = None,
        visible: bool = True,
        disabled: bool = False,
        theme: Optional[ComboBoxTheme] = ThemeManager.ComboBoxThemes.DEFAULT,
        label: Optional[str] = None,
        hint_text: Optional[str] = "Sélectionnez une option...",
        helper_text: Optional[str] = None,
        error_messages: Optional[Dict[str, str]] = None,
        required: bool = False,
        options: List = None,
        value: Any = None,
        on_change: Optional[Callable] = None,
        on_focus: Optional[Callable] = None,
        on_blur: Optional[Callable] = None,
        parent=None,
    ) -> None:
        default_errors = {
            "required": "Veuillez choisir une option",
            "invalid": "Sélection invalide.",
        }
        if error_messages:
            default_errors.update(error_messages)
        # Store combobox specific attributes
        self._options = options or []
        self._initial_value = value

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
            error_messages=default_errors,
            required=required,
            on_change=on_change,
            on_focus=on_focus,
            on_blur=on_blur,
            parent=parent,
        )

    def _create_form_field(self) -> None:
        """Create and configure the ComboBox widget."""
        self.combobox_layout = QHBoxLayout()
        self.combobox_layout.setSpacing(2)
        self.combobox_layout.setContentsMargins(0, 0, 0, 0)

        # Create ComboBox
        self.combobox = QComboBox(self)
        self._form_field_widget = self.combobox

        # Configure editable mode and insert policy
        self.combobox.setEditable(True)
        self.combobox.setInsertPolicy(QComboBox.NoInsert)

        # Configure dimensions
        if self._width and self._height:
            self.combobox.setFixedSize(self._width, self._height)
        elif self._height:
            self.combobox.setFixedHeight(self._height)

        # Setup completer
        self.completer = QCompleter(self._options, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.combobox.setCompleter(self.completer)

        # Set options
        self.set_options(self._options)

        # Set initial value if provided
        if self._initial_value is not None:
            self.set_value(self._initial_value)

        # Connect signals
        self.combobox.currentIndexChanged.connect(self.on_value_changed)
        self._form_field_widget.installEventFilter(self)

        # Add to layout
        self.combobox_layout.addWidget(self.combobox)
        self.combobox_layout.addStretch(1)
        self.main_layout.addLayout(self.combobox_layout)
    
    def set_options(self, options: List) -> None:
        """Set ComboBox options with hint text."""
        self.combobox.clear()
        self.combobox.addItem(self._hint_text, None)

        for item in options:
            if isinstance(item, tuple) and len(item) == 2:
                label, user_data = item
            elif isinstance(item, dict):
                label = item.get("text", "Unknown")
                user_data = item.get("user_data", None)
            elif hasattr(item, "title") and hasattr(item, "id"):
                label = item.title
                user_data = item.id
            else:
                label = str(item)
                user_data = item

            self.combobox.addItem(str(label), user_data)

        self._options = [
            self.combobox.itemText(i) for i in range(1, self.combobox.count())
        ]
        self.completer.setModel(QStringListModel(self._options))

    def get_value(self) -> Any:
        """Get the current selected value."""
        index = self.combobox.currentIndex()
        if index <= 0:  # No selection or hint text
            return None
        return self.combobox.itemData(index)

    def set_value(self, value: Any) -> bool:
        """Set the current value."""
        if value is None:
            self.reset()
            return True

        # Try to find in userData
        for i in range(self.combobox.count()):
            if self.combobox.itemData(i) == value:
                self.combobox.setCurrentIndex(i)
                return True

        # Try to find in displayed text
        index = self.combobox.findText(str(value))
        if index >= 0:
            self.combobox.setCurrentIndex(index)
            return True

        return False

    def reset(self) -> None:
        """Reset to initial state."""
        super().reset()
        self.combobox.setCurrentIndex(0)

    def is_valid(self) -> bool:
        """
        Validate the ComboBox selection.
        
        Checks:
        - If field is required, ensures a valid selection is made (not the hint text)
        - Ensures selected value exists in options list
        
        Returns:
            bool: True if field content is valid, False otherwise
        """
        value = self.get_value()
        current_text = self.current_text
        
        if self._required:
            if value is None or current_text == self._hint_text:
                self.show_error(self._error_messages["required"])
                return False
        
        if current_text and current_text != self._hint_text:
            is_valid_option = False
            
            for i in range(self.combobox.count()):
                if (self.combobox.itemText(i) == current_text or 
                    self.combobox.itemData(i) == value):
                    is_valid_option = True
                    break
                    
            if not is_valid_option:
                self.show_error(self._error_messages["invalid"])
                return False
        
        self.hide_error()
        return True

    @property
    def current_text(self) -> str:
        """Get the current displayed text."""
        return self.combobox.currentText().strip()

    @property
    def current_index(self) -> int:
        """Get the current selected index."""
        return self.combobox.currentIndex()
