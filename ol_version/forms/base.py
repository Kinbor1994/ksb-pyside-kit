from enum import Enum
from typing import Dict, Any, Optional, List, Callable, TypeVar, Generic
from dataclasses import dataclass

from ..core.utils import set_app_icon

from ..core.commons import QDialog, QGridLayout, QVBoxLayout, QHBoxLayout, Signal, Qt, QWidget

from ..widgets import Button, Text, Separator
from ..core.base_form_field import BaseFormField
from ..core.themes.themes import ThemeManager, FormTheme
from ..core.exceptions import ValidationError

T = TypeVar("T", bound=BaseFormField)


class FieldAlignment(str, Enum):
    """Field alignment options in form layout."""

    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"
    FILL = "fill"  # Fill available space


@dataclass
class FieldPosition:
    """
    Field position and layout configuration in form grid.

    Args:
        row (int): Row index in grid
        column (int): Column index in grid
        alignment (FieldAlignment): Field alignment in cell
        colspan (int): Number of columns to span
    """

    row: int
    column: int
    alignment: FieldAlignment = FieldAlignment.FILL
    colspan: int = 1


class FormBase(QWidget, Generic[T]):
    """
    Base class for all forms.

    A form widget that manages form fields, validation, and data handling.

    Signals:
        submitted (dict): Emitted when form is submitted with valid data
        validation_failed (dict): Emitted when validation fails with errors
        cancelled: Emitted when form is cancelled

    Args:
        title (Optional[str]): Form title
        parent (Optional[QWidget]): Parent widget
        show_buttons (bool): Whether to show form buttons
        submit_text (str): Text for submit button
        cancel_text (str): Text for cancel button
        theme (Optional[FormTheme]): Form theme configuration
    """

    # Signals
    submitted = Signal(dict)
    validation_failed = Signal(dict)
    cancelled = Signal()

    def __init__(
        self,
        title: Optional[str] = None,
        parent: Optional[QWidget] = None,
        show_buttons: bool = True,
        submit_text: str = "Enregistrer",
        cancel_text: str = "Fermer",
        theme: Optional[FormTheme] = ThemeManager.FormThemes.DEFAULT,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("form_container")

        # Initialize attributes
        self.title = title
        self._fields: Dict[str, T] = {}
        self._validators: List[Callable] = []
        self._errors: Dict[str, List[str]] = {}
        self._theme = theme

        # Setup layouts
        self._form_layout = QGridLayout()
        self._form_layout.setSpacing(2)
        self._form_layout.setContentsMargins(0, 0, 0, 0)
        
        self._main_layout = QVBoxLayout()
        self._main_layout.setSpacing(2)
        self._main_layout.setContentsMargins(5, 5, 5, 5)
        

        ## Set title if provided
        if self.title:
            self.title_label = Text(value=self.title, align="left", theme=ThemeManager.TextThemes.H3_PRIMARY)
            self._main_layout.addWidget(self.title_label)
            
            # Add a separator line below the title
            self.separator = Separator(orientation="horizontal", theme=ThemeManager.SeparatorThemes.DEFAULT)
            self._main_layout.addWidget(self.separator)
            
        self._main_layout.addLayout(self._form_layout)
        
        # Add buttons if requested
        if show_buttons:
            self._setup_buttons(submit_text, cancel_text)
        
        # Error message
        self.error_message = Text(
            value="",
            theme=ThemeManager.TextThemes.LABEL_NB,
        )
        self.error_message.hide()
        self._main_layout.addWidget(self.error_message)
        
        self._main_layout.addStretch(1)
        
        self.setLayout(self._main_layout)
        self._apply_theme(self._theme)

    def _setup_buttons(self, submit_text: str, cancel_text: str) -> None:
        """Setup form buttons using custom Button widget."""
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.submit_button = Button(
            text=submit_text,
            on_click=self._handle_submit,
            theme=self._theme.submit_button_theme,
            parent=self,
        )
        button_layout.addWidget(self.submit_button)

        self.cancel_button = Button(
            text=cancel_text,
            on_click=self._handle_cancel,
            theme=self._theme.cancel_button_theme,
            parent=self,
        )
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch(1)
        self._main_layout.addLayout(button_layout)

    def add_field(self, field: T, position: Optional[FieldPosition] = None) -> None:
        """
        Add a field to the form.

        Args:
            field (BaseFormField): Form field widget
            position (Optional[FieldPosition]): Grid position and layout configuration
        """
        name = field._key
        
        if not name:
            raise ValueError("Field must have a unique name (key)")
        
        if name in self._fields:
            raise ValueError(f"Field '{name}' already exists")

        self._fields[name] = field
        field.setParent(self)

        alignment_map = {
            FieldAlignment.LEFT: Qt.AlignmentFlag.AlignLeft,
            FieldAlignment.RIGHT: Qt.AlignmentFlag.AlignRight,
            FieldAlignment.CENTER: Qt.AlignmentFlag.AlignCenter,
            FieldAlignment.FILL: Qt.AlignmentFlag.AlignHCenter
            | Qt.AlignmentFlag.AlignVCenter,
        }

        if position:
            self._form_layout.addWidget(
                field,
                position.row,
                position.column,
                1,
                position.colspan,
                alignment_map[position.alignment],
            )
        else:
            row = self._form_layout.rowCount()
            self._form_layout.addWidget(
                field,
                row,
                0,
                1,
                self._form_layout.columnCount() or 2,
                Qt.AlignmentFlag.AlignLeft,
            )

    def add_validator(self, validator: Callable[["FormBase"], None]) -> None:
        """
        Add a custom form-level validator.

        Args:
            validator: Validation function that raises ValidationError on failure
        """
        self._validators.append(validator)

    def get_field(self, name: str) -> Optional[T]:
        """Get field by name."""
        return self._fields.get(name)

    def get_data(self) -> Dict[str, Any]:
        """Get form data as dictionary."""
        return {name: field.get_value() for name, field in self._fields.items()}

    def set_data(self, data: Dict[str, Any]) -> None:
        """Set form data from dictionary."""
        for name, value in data.items():
            if field := self._fields.get(name):
                field.set_value(value)

    def _is_valid(self) -> bool:
        """
        Validate all form fields and run form-level validation.
        
        Returns:
            bool: True if form is valid
        """
        # Clear previous errors
        self._errors.clear()
        self.error_message.text = ""
        
        
        fields_valid = True
        for name, field in self._fields.items():
            if hasattr(field, "is_valid"):
                if not field.is_valid():
                    fields_valid = False
        
        
        if fields_valid and self._validators:
            try:
                for validator in self._validators:
                    validator(self)
            except ValidationError as e:
                fields_valid = False
                self._errors["__form__"] = [str(e)]
                self.show_error(str(e))
        
        return fields_valid

    def show_error(self, message: str):
        """Display error message"""
        self.error_message.text = message
        self.error_message.show()

    def clear(self) -> None:
        """Clear all form fields and errors."""
        for field in self._fields.values():
            field.clear_content()
        self.error_message.hide()

    def _handle_submit(self) -> None:
        """
        Handle form submission.
        
        Validates all fields and emits appropriate signals:
        - submitted: if all validations pass
        - validation_failed: if any validation fails
        """
        """Handle form submission."""
        if self._is_valid():
            self.submitted.emit(self.get_data())
        else:
            self.validation_failed.emit(self._errors)

    def _handle_cancel(self) -> None:
        """Handle form cancellation."""
        self.cancelled.emit()

    def _apply_theme(self, theme: ThemeManager) -> None:
        """
        Apply a theme to the widget.

        Args:
            theme: Theme configuration to apply
        """
        if theme and hasattr(theme, "get_stylesheet"):
            self.setStyleSheet(theme.get_stylesheet())
            self._theme = theme

        self.parent().setStyleSheet(f"""background-color: {theme.background_color}; """)

class FormModalBase(QDialog, Generic[T]):
    """
    Base class for all model forms.

    A form modal that manages form fields, validation, and data handling.

    Signals:
        submitted (dict): Emitted when form is submitted with valid data
        validation_failed (dict): Emitted when validation fails with errors
        cancelled: Emitted when form is cancelled

    Args:
        title (Optional[str]): Form title
        parent (Optional[QWidget]): Parent widget
        show_buttons (bool): Whether to show form buttons
        submit_text (str): Text for submit button
        cancel_text (str): Text for cancel button
        theme (Optional[FormTheme]): Form theme configuration
    """

    # Signals
    submitted = Signal(dict)
    validation_failed = Signal(dict)
    cancelled = Signal()

    def __init__(
        self,
        title: Optional[str] = None,
        parent: Optional[QWidget] = None,
        show_buttons: bool = True,
        submit_text: str = "Enregistrer",
        cancel_text: str = "Fermer",
        theme: Optional[FormTheme] = ThemeManager.FormThemes.DEFAULT,
    ) -> None:
        super().__init__(parent)

        # Configure dialog
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        set_app_icon(app=self)
        
        # Initialize attributes
        self.title = title
        self._fields: Dict[str, T] = {}
        self._validators: List[Callable] = []
        self._errors: Dict[str, List[str]] = {}
        self._theme = theme

        self.setWindowTitle(self.title or "")
        
        # Setup layouts
        self._form_layout = QGridLayout()
        self._form_layout.setSpacing(2)
        self._form_layout.setContentsMargins(0, 0, 0, 0)
        
        self._main_container = QWidget()
        self._main_container.setObjectName("form_container")
        self._main_layout = QVBoxLayout(self._main_container)
        self._main_layout.setSpacing(2)
        self._main_layout.setContentsMargins(5, 5, 5, 5)
        

        ## Set title if provided
        if self.title:
            self.title_label = Text(value=self.title, align="left", theme=ThemeManager.TextThemes.H3_PRIMARY)
            self._main_layout.addWidget(self.title_label)
            
            # Add a separator line below the title
            self.separator = Separator(orientation="horizontal", theme=ThemeManager.SeparatorThemes.DEFAULT)
            self._main_layout.addWidget(self.separator)
            
        self._main_layout.addLayout(self._form_layout)
        
        # Add buttons if requested
        if show_buttons:
            self._setup_buttons(submit_text, cancel_text)
        
        # Error message
        self.error_message = Text(
            value="",
            theme=ThemeManager.TextThemes.LABEL_NB,
        )
        self.error_message.hide()
        self._main_layout.addWidget(self.error_message)
        
        self._main_layout.addStretch(1)
        
        self.setLayout(self._main_layout)
        self._apply_theme(self._theme)

    def _setup_buttons(self, submit_text: str, cancel_text: str) -> None:
        """Setup form buttons using custom Button widget."""
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.submit_button = Button(
            text=submit_text,
            on_click=self._handle_submit,
            theme=self._theme.submit_button_theme,
            parent=self,
        )
        button_layout.addWidget(self.submit_button)

        self.cancel_button = Button(
            text=cancel_text,
            on_click=self._handle_cancel,
            theme=self._theme.cancel_button_theme,
            parent=self,
        )
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch(1)
        self._main_layout.addLayout(button_layout)

    def add_field(self, field: T, position: Optional[FieldPosition] = None) -> None:
        """
        Add a field to the form.

        Args:
            field (BaseFormField): Form field widget
            position (Optional[FieldPosition]): Grid position and layout configuration
        """
        name = field._key
        
        if not name:
            raise ValueError("Field must have a unique name (key)")
        
        if name in self._fields:
            raise ValueError(f"Field '{name}' already exists")

        self._fields[name] = field
        field.setParent(self)

        alignment_map = {
            FieldAlignment.LEFT: Qt.AlignmentFlag.AlignLeft,
            FieldAlignment.RIGHT: Qt.AlignmentFlag.AlignRight,
            FieldAlignment.CENTER: Qt.AlignmentFlag.AlignCenter,
            FieldAlignment.FILL: Qt.AlignmentFlag.AlignHCenter
            | Qt.AlignmentFlag.AlignVCenter,
        }

        if position:
            self._form_layout.addWidget(
                field,
                position.row,
                position.column,
                1,
                position.colspan,
                alignment_map[position.alignment],
            )
        else:
            row = self._form_layout.rowCount()
            self._form_layout.addWidget(
                field,
                row,
                0,
                1,
                self._form_layout.columnCount() or 2,
                Qt.AlignmentFlag.AlignLeft,
            )

    def add_validator(self, validator: Callable[["FormBase"], None]) -> None:
        """
        Add a custom form-level validator.

        Args:
            validator: Validation function that raises ValidationError on failure
        """
        self._validators.append(validator)

    def get_field(self, name: str) -> Optional[T]:
        """Get field by name."""
        return self._fields.get(name)

    def get_data(self) -> Dict[str, Any]:
        """Get form data as dictionary."""
        return {name: field.get_value() for name, field in self._fields.items()}

    def set_data(self, data: Dict[str, Any]) -> None:
        """Set form data from dictionary."""
        for name, value in data.items():
            if field := self._fields.get(name):
                field.set_value(value)

    def _is_valid(self) -> bool:
        """
        Validate all form fields and run form-level validation.
        
        Returns:
            bool: True if form is valid
        """
        # Clear previous errors
        self._errors.clear()
        self.error_message.text = ""
        
        
        fields_valid = True
        for name, field in self._fields.items():
            if hasattr(field, "is_valid"):
                if not field.is_valid():
                    fields_valid = False
        
        
        if fields_valid and self._validators:
            try:
                for validator in self._validators:
                    validator(self)
            except ValidationError as e:
                fields_valid = False
                self._errors["__form__"] = [str(e)]
                self.show_error(str(e))
        
        return fields_valid

    def show_error(self, message: str):
        """Display error message"""
        self.error_message.text = message
        self.error_message.show()

    def clear(self) -> None:
        """Clear all form fields and errors."""
        for field in self._fields.values():
            field.clear_content()
        self.error_message.hide()

    def _handle_submit(self) -> None:
        """
        Handle form submission.
        
        Validates all fields and emits appropriate signals:
        - submitted: if all validations pass
        - validation_failed: if any validation fails
        """
        """Handle form submission."""
        if self._is_valid():
            self.submitted.emit(self.get_data())
        else:
            self.validation_failed.emit(self._errors)

    def _handle_cancel(self) -> None:
        """Handle form cancellation."""
        self.cancelled.emit()

    def _apply_theme(self, theme: ThemeManager) -> None:
        """
        Apply a theme to the widget.

        Args:
            theme: Theme configuration to apply
        """
        if theme and hasattr(theme, "get_stylesheet"):
            self.setStyleSheet(theme.get_stylesheet())
            self._theme = theme