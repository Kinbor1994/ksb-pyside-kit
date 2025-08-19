from typing import Optional, Union, Dict, Callable
from datetime import datetime

from ..core.commons import QDateEdit, QDate, QHBoxLayout
from ..core.base_form_field import BaseFormField
from ..core.themes.themes import ThemeManager, DateFieldTheme

class DateField(BaseFormField):
    """
    Form field widget for date input with extended functionality.
    
    Args:
        key (str, optional): Unique widget identifier
        width (int, optional): Widget width in pixels
        height (int, optional): Widget height in pixels
        tooltip (str, optional): Hover tooltip text
        visible (bool): Initial visibility state
        disabled (bool): Initial disabled state
        theme (DateFieldTheme): Theme configuration
        label (str, optional): Label text
        helper_text (str, optional): Helper text below field
        error_messages (Dict[str, str], optional): Custom error messages
        required (bool): Whether field is required
        format_date (str, optional): Date display format
        min_date (Union[QDate, datetime], optional): Minimum selectable date
        max_date (Union[QDate, datetime], optional): Maximum selectable date
        value (Union[QDate, datetime], optional): Initial date value
        calendar_popup (bool): Show calendar popup
        on_change (Callable, optional): Date change callback
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
        theme: DateFieldTheme = ThemeManager.DateFieldThemes.DEFAULT,
        label: Optional[str] = None,
        helper_text: Optional[str] = None,
        error_messages: Optional[Dict[str, str]] = None,
        required: bool = False,
        format_date: str = "dd/MM/yyyy",
        min_date: Optional[Union[QDate, datetime]] = None,
        max_date: Optional[Union[QDate, datetime]] = None,
        value: Optional[Union[QDate, datetime]] = None,
        calendar_popup: bool = True,
        on_change: Optional[Callable] = None,
        on_focus: Optional[Callable] = None,
        on_blur: Optional[Callable] = None,
        parent = None,
    ) -> None:
        # Store date field specific attributes
        self._format_date = format_date
        self._min_date = self._convert_to_qdate(min_date) if min_date else None
        self._max_date = self._convert_to_qdate(max_date) if max_date else None
        self._initial_value = self._convert_to_qdate(value) if value else None
        self._calendar_popup = calendar_popup

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
            helper_text=helper_text,
            error_messages=error_messages,
            required=required,
            on_change=on_change,
            on_focus=on_focus,
            on_blur=on_blur,
            parent=parent
        )

    def _create_form_field(self) -> None:
        """Create and configure the QDateEdit widget."""
        self.date_layout = QHBoxLayout()
        self.date_layout.setSpacing(2)
        self.date_layout.setContentsMargins(0, 0, 0, 0)

        # Create QDateEdit
        self.date_edit = QDateEdit(self)
        self._form_field_widget = self.date_edit
        
        # Configure dimensions
        if self._width and self._height:
            self.date_edit.setFixedSize(self._width, self._height)
        elif self._height:
            self.date_edit.setFixedHeight(self._height)

        # Configure date settings
        self.date_edit.setDisplayFormat(self._format_date)
        self.date_edit.setCalendarPopup(self._calendar_popup)

        if self._min_date:
            self.date_edit.setMinimumDate(self._min_date)
        if self._max_date:
            self.date_edit.setMaximumDate(self._max_date)
        if self._initial_value:
            self.date_edit.setDate(self._initial_value)

        # Connect signals
        self.date_edit.dateChanged.connect(self.on_value_changed)
        self._form_field_widget.installEventFilter(self)

        # Add to layout
        self.date_layout.addWidget(self.date_edit)
        self.date_layout.addStretch(1)
        self.main_layout.addLayout(self.date_layout)

    def _convert_to_qdate(self, date: Union[QDate, datetime]) -> QDate:
        """Convert datetime to QDate if needed."""
        if isinstance(date, datetime):
            return QDate(date.year, date.month, date.day)
        return date

    def get_date_as_string(self, format_str: Optional[str] = None) -> str:
        """Get date as formatted string."""
        date = self.date_edit.date()
        if format_str:
            return date.toString(format_str)
        return date.toString(self.date_edit.displayFormat())

    def is_valid(self) -> bool:
        """Validate the date field."""
        current_date = self.date_edit.date()
        
        # Required field validation
        if self._required and current_date.isNull():
            self.show_error(self._error_messages["required"])
            return False
        
        # Date validity check
        if not current_date.isValid():
            self.show_error("Date invalide")
            return False
            
        # Min/Max date validation
        min_date = self.date_edit.minimumDate()
        max_date = self.date_edit.maximumDate()
        
        if current_date < min_date:
            self.show_error(f"La date doit être après le {self.get_date_as_string(min_date)}")
            return False
            
        if current_date > max_date:
            self.show_error(f"La date doit être avant le {self.get_date_as_string(max_date)}")
            return False

        self.hide_error()
        return True

    def get_value(self) -> datetime:
        """Get current date as Python datetime."""
        return self.date_edit.date().toPython()

    def set_value(self, value: Union[QDate, datetime, str, None]) -> bool:
        """Set the date value."""
        if value is None:
            self.date_edit.setDate(self.date_edit.minimumDate())
            return True
            
        try:
            if isinstance(value, QDate):
                if value.isValid():
                    self.date_edit.setDate(value)
                    return True
                    
            elif isinstance(value, datetime):
                date = QDate(value.year, value.month, value.day)
                self.date_edit.setDate(date)
                return True
                
            elif isinstance(value, str):
                date = QDate.fromString(value, self._format_date)
                if date.isValid():
                    self.date_edit.setDate(date)
                    return True
                
        except Exception as e:
            print(f"Error setting date value: {e}")
            return False
            
        return False

    def clear_content(self) -> None:
        """Clear the date field."""
        super().clear_content()
        self.date_edit.setDate(self.date_edit.minimumDate())
