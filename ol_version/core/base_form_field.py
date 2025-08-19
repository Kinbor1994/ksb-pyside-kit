from typing import Optional, Any, Callable, Dict

from ..core.commons import QEvent, QObject
from .base_widget import BaseWidget
from ..widgets.text import Text
from .themes.themes import ThemeManager

class BaseFormField(BaseWidget):
    """
    Base class for all form field widgets in the application.
    Provides common functionality for form fields like:
        
    - Label support
    - Value management
    - Validation
    - Error handling
    - Focus management
    - Change event handling
    
    Args:
        key (str, optional): Unique identifier for the widget
        width (int, optional): Widget width in pixels
        height (int, optional): Widget height in pixels
        tooltip (str, optional): Hover tooltip text
        visible (bool, optional): Initial visibility state. Defaults to True
        disabled (bool, optional): Initial disabled state. Defaults to False
        theme (Any, optional): Theme configuration to apply
        label (str, optional): Label text displayed above the form field
        hint_text (str, optional): Placeholder text displayed in the widget
        helper_text (str, optional): Helper text displayed below the widget
        error_messages (Dict, optional): Custom error messages for validation
        required (bool, optional): Whether the field is required. Defaults to False
        on_change (Callable, optional): Callback for value change event
        on_focus (Callable, optional): Callback for focus event
        on_blur (Callable, optional): Callback for blur event
        parent (QWidget, optional): Parent widget. Defaults to None
    """

    def __init__(
        self,
        key: Optional[str] = None,
        width: Optional[int] = 200,
        height: Optional[int] = 40,
        tooltip: Optional[str] = None,
        visible: bool = True,
        disabled: bool = False,
        theme: Optional[ThemeManager] = None,
        label: Optional[str] = None,
        hint_text: Optional[str] = None,
        helper_text: Optional[str] = None,
        error_messages: Optional[Dict[str, str]] = None,
        required: bool = False,
        on_change: Optional[Callable] = None,
        on_focus: Optional[Callable] = None,
        on_blur: Optional[Callable] = None,
        parent=None,
    ) -> None:
        """Initialize the base form field with common functionality."""
        
        
        # Store form field specific attributes
        self._label_text = label
        self._hint_text = hint_text
        self._helper_text = helper_text
        self._required = required
        self._on_change = on_change
        self._on_focus = on_focus
        self._on_blur = on_blur
        self._form_field_widget = None
        
        super().__init__(
            key=key,
            width=width,
            height=height,
            tooltip=tooltip,
            visible=visible,
            disabled=disabled,
            theme=theme,
            parent=parent,
        )
        
        # Default error messages
        self._default_error_messages = {
            "required": "Ce champ est requis",
            "invalid": "Valeur invalide",
        }
        
        # Merge default and custom error messages
        self._error_messages = self._default_error_messages.copy()
        if error_messages:
            self._error_messages.update(error_messages)
        
        # Internal state tracking
        self._has_error = False
        self._is_dirty = False

    def _setup_ui(self) -> None:
        """
        Initialize the UI elements for the form field.
        """
        
        # Création des éléments du formulaire
        self._create_label()
        self._create_form_field()
        self._create_helper_text()
        self._create_error_text()
        self.main_layout.addStretch(1)
        
    def _create_label(self) -> None:
        """Create label widget if label text is provided."""
        if self._required and self._label_text:
            self._label_text += " (*)"
            
        if self._label_text:
            self.label = Text(
                value=self._label_text,
                theme=ThemeManager.TextThemes.LABEL,
            )
            self.main_layout.addWidget(self.label)
    
    def _create_form_field(self) -> None:
        """
        Create the actual form field widget.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _create_form_field()")
    
    def _create_helper_text(self) -> None:
        """Create helper text widget if helper text is provided."""
        if self._helper_text:
            self.helper_label = Text(
                value=self._helper_text,
                theme=ThemeManager.TextThemes.HELPER,
            )
            self.main_layout.addWidget(self.helper_label)
    
    def _create_error_text(self) -> None:
        """Create error text widget."""
        self.error_label = Text(
            value="",
            theme=ThemeManager.TextThemes.ERROR,
        )
        self.main_layout.addWidget(self.error_label)
    
    def show_error(self, message: str) -> None:
        """
        Display an error message.
        
        Args:
            message (str): Error message to display
        """
        self._has_error = True
        self.error_label.text = message
        # Additional styling for error state can be applied here
    
    def hide_error(self) -> None:
        """Hide the error message."""
        if self._has_error:
            self._has_error = False
            self.error_label.text = ""
            # Additional styling for normal state can be applied here
    
    def is_valid(self) -> bool:
        """
        Validate the field based on validation rules.
        This method should be extended by subclasses for specific validation.
        
        Returns:
            bool: True if valid, False otherwise
        """
        pass
            
    def get_value(self) -> Any:
        """
        Get the current value of the field.
        This method should be implemented by subclasses.
        
        Returns:
            Any: The current value
        """
        raise NotImplementedError("Subclasses must implement get_value()")
    
    def set_value(self, value: Any) -> bool:
        """
        Set the value of the field.
        This method should be implemented by subclasses.
        
        Args:
            value: The value to set
            
        Returns:
            bool: True if value was successfully set, False otherwise
        """
        raise NotImplementedError("Subclasses must implement set_value()")
    
    def reset(self) -> None:
        """
        Reset the field to its initial state.
        This method should be extended by subclasses.
        """
        self._is_dirty = False
        self._has_error = False
        self.hide_error()
    
    def clear_content(self) -> None:
        """
        Clear the field content.
        This method should be implemented by subclasses.
        """
        self.reset()
    
    def on_focus_in(self) -> None:
        """Handle focus in event."""
        if self._on_focus:
            self._on_focus()
    
    def on_focus_out(self) -> None:
        """Handle focus out event."""
        if self._on_blur:
            self._on_blur()
        else:
            self.is_valid()
    
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        """
        Handle focus events for form fields.

        Args:
            watched (QObject): The object being watched
            event (QEvent): The event that occurred

        Returns:
            bool: True if the event was handled, False otherwise
        """
        # Check if the event is from the form field widget
        if watched == self._form_field_widget:
            # Handle focus events
            if event.type() == QEvent.FocusOut:
                self.on_focus_out()

            if event.type() == QEvent.FocusIn:
                self.on_focus_in()

        return super().eventFilter(watched, event)
        
    def on_value_changed(self, value: Any) -> None:
        """
        Handle value change event.
        
        Args:
            value: The new value
        """
        self._is_dirty = True
        
        if self._on_change:
            self._on_change(value)
        self.is_valid()
    
    @property
    def value(self) -> Any:
        """
        Property getter for the field value.
        
        Returns:
            Any: The current value
        """
        return self.get_value()
    
    @value.setter
    def value(self, value: Any) -> None:
        """
        Property setter for the field value.
        
        Args:
            value: The value to set
        """
        self.set_value(value)
    
    @property
    def required(self) -> bool:
        """Get the required state of the field."""
        return self._required
    
    @required.setter
    def required(self, value: bool) -> None:
        """Set the required state of the field."""
        self._required = value
    
    @property
    def error_messages(self) -> Dict[str, str]:
        """Get the error messages dictionary."""
        return self._error_messages
    
    @error_messages.setter
    def error_messages(self, messages: Dict[str, str]) -> None:
        """
        Update the error messages dictionary.
        
        Args:
            messages: Dictionary of error messages to update
        """
        if messages:
            self._error_messages.update(messages)