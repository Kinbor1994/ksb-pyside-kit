from enum import Enum
import re
from typing import Optional, Any, Dict, Callable
from ..core.commons import QLineEdit, QHBoxLayout

from ..core.base_form_field import BaseFormField
from .button import IconButton
from ..core.themes.themes import TextFieldTheme, ThemeManager

class InputFilter(Enum):
    """Available input filter types."""
    TEXT = "text"
    NUMERIC = "numeric"
    EMAIL = "email"

class TextFieldBase(BaseFormField):
    """
    Base widget for text input fields with integrated validation.
    
    Args:
        key (str, optional): Unique widget identifier
        width (int, optional): Widget width in pixels
        height (int, optional): Widget height in pixels
        tooltip (str, optional): Hover tooltip text
        visible (bool): Initial visibility state
        disabled (bool): Initial disabled state
        theme (TextFieldTheme): Field theme configuration
        label (str, optional): Label text
        hint_text (str, optional): Placeholder text
        helper_text (str, optional): Helper text below field
        error_messages (Dict[str, str], optional): Custom error messages
        required (bool): Whether field is required
        value (str, optional): Initial value
        password (bool): Password mode
        can_reveal_password (bool): Allow password visibility toggle
        read_only (bool): Read-only mode
        input_filter (InputFilter): Input filter type
        on_change (Callable, optional): Value change callback
        on_focus (Callable, optional): Focus gained callback
        on_blur (Callable, optional): Focus lost callback
        parent (QWidget, optional): Parent widget
        min_value (Optional[float]): Minimum value for numeric fields
        max_value (Optional[float]): Maximum value for numeric fields
        min_length (Optional[int]): Minimum text length
        max_length (Optional[int]): Maximum text length
        validation_pattern (Optional[str]): Regex pattern for custom validation
        validation_message (Optional[str]): Error message for pattern validation
    """

    def __init__(
        self,
        key: Optional[str] = None,
        width: Optional[int] = 300,
        height: Optional[int] = 40,
        tooltip: Optional[str] = None,
        visible: bool = True,
        disabled: bool = False,
        theme: TextFieldTheme = ThemeManager.TextFieldThemes.DEFAULT,
        label: Optional[str] = None,
        hint_text: Optional[str] = None,
        helper_text: Optional[str] = None,
        error_messages: Optional[Dict[str, str]] = None,
        required: bool = False,
        value: Optional[str] = None,
        password: bool = False,
        can_reveal_password: bool = False,
        read_only: bool = False,
        input_filter: InputFilter = InputFilter.TEXT,
        on_change: Optional[Callable] = None,
        on_focus: Optional[Callable] = None,
        on_blur: Optional[Callable] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        validation_pattern: Optional[str] = None,
        validation_message: Optional[str] = None,
        parent = None,
    ) -> None:
        # Default error messages in French for end users
        default_errors = {
            "required": "Ce champ est requis",
            "email": "Adresse e-mail invalide",
            "numeric": "Seuls les chiffres sont autorisés",
            "pattern": "Format invalide",  # Default pattern message
            "min_value": lambda x: f"La valeur doit être supérieure ou égale à {x}",
            "max_value": lambda x: f"La valeur doit être inférieure ou égale à {x}",
            "min_length": lambda x: f"Le texte doit contenir au moins {x} caractères",
            "max_length": lambda x: f"Le texte ne doit pas dépasser {x} caractères",
        }
        if error_messages:
            default_errors.update(error_messages)

        # Store text field specific attributes
        self._min_value = min_value
        self._max_value = max_value
        self._password = password
        self._can_reveal_password = can_reveal_password
        self._read_only = read_only
        self._input_filter = input_filter
        self._initial_value = value
        self._min_length = min_length
        self._max_length = max_length
        self._validation_pattern = validation_pattern
        self._validation_message = validation_message or default_errors["pattern"]

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
            parent=parent
        )
        
    def _create_form_field(self) -> None:
        """Create and configure the QLineEdit widget."""
        self.input_layout = QHBoxLayout()
        self.input_layout.setSpacing(2) 
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        # Create the QLineEdit
        self.line_edit = QLineEdit(self)
        self._form_field_widget = self.line_edit
        
        # Configure dimensions
        if self._width and self._height:
            width = self._width - 30 if self._password and self._can_reveal_password else self._width
            self.line_edit.setFixedSize(width, self._height)
        elif self._height:
            self.line_edit.setFixedHeight(self._height)

        # Configure options
        self.line_edit.setReadOnly(self._read_only)
        if self._hint_text:
            self.line_edit.setPlaceholderText(self._hint_text)
        if self._initial_value:
            self.set_value(self._initial_value)

        self.input_layout.addWidget(self.line_edit)
        
        # Setup password mode if needed
        if self._password:
            self.line_edit.setEchoMode(QLineEdit.Password)
            if self._can_reveal_password:
                self._setup_reveal_button()

        # Apply input filter
        self._setup_input_filter()

        # Connect signals
        self.line_edit.textChanged.connect(self.on_value_changed)
        self._form_field_widget.installEventFilter(self)

        self.input_layout.addStretch(1)
        self.main_layout.addLayout(self.input_layout)

    def _setup_reveal_button(self) -> None:
        """Set up password reveal toggle button."""
        self.reveal_button = IconButton(
            icon="fa5s.eye",
            width=24,
            height=24,
            theme=ThemeManager.ButtonThemes.DARK,
            on_click=self._toggle_password_visibility,
            parent=self
        )
        self.reveal_button._button.setCheckable(False)
        self.input_layout.addWidget(self.reveal_button)

    def _toggle_password_visibility(self) -> None:
        """Toggle password visibility state."""
        is_visible = self.line_edit.echoMode() == QLineEdit.Normal
        self.line_edit.setEchoMode(
            QLineEdit.Password if is_visible else QLineEdit.Normal
        )
        self.reveal_button.set_icon(
            "fa5s.eye-slash" if is_visible else "fa5s.eye"
        )

    def _setup_input_filter(self) -> None:
        """Set up input filtering based on type."""
        if self._input_filter == InputFilter.NUMERIC:
            self.line_edit.textChanged.connect(self._validate_numeric)
        elif self._input_filter == InputFilter.EMAIL:
            self.line_edit.textChanged.connect(self._validate_email)

    def _validate_email(self, text: str) -> bool:
        """Validate email format."""
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if text and not re.match(email_regex, text):
            self.show_error(self._error_messages["email"])
            return False
        return True

    def _validate_numeric(self, text: str) -> bool:
        """
        Validates if the input contains a valid numeric value within specified range.

        Args:
            text (str): The text input to validate.

        Returns:
            bool: True if the input is valid, False otherwise.
        """
        if not text:
            return True

        # Validate numeric format
        numeric_regex = r"^-?\d+(\.\d+)?$"
        if not re.match(numeric_regex, text):
            self.show_error(self._error_messages["numeric"])
            return False

        # Validate range if specified
        try:
            value = float(text)
            
            if self._min_value is not None and value < self._min_value:
                self.show_error(self._error_messages["min_value"](self._min_value))
                return False
                
            if self._max_value is not None and value > self._max_value:
                self.show_error(self._error_messages["max_value"](self._max_value))
                return False
                
            return True
            
        except ValueError:
            self.show_error(self._error_messages["numeric"])
            return False

    def _validate_text_length(self, text: str) -> bool:
        """
        Validates if the text length is within specified bounds.

        Args:
            text (str): The text to validate.

        Returns:
            bool: True if the text length is valid, False otherwise.
        """
        if not text:
            return True

        if self._min_length and len(text) < self._min_length:
            self.show_error(self._error_messages["min_length"](self._min_length))
            return False

        if self._max_length and len(text) > self._max_length:
            self.show_error(self._error_messages["max_length"](self._max_length))
            return False

        return True

    def _validate_pattern(self, text: str) -> bool:
        """
        Validates text against custom pattern if specified.

        Args:
            text (str): Text to validate

        Returns:
            bool: True if pattern matches or no pattern specified
        """
        if not text or not self._validation_pattern:
            return True

        if not re.match(self._validation_pattern, text):
            self.show_error(self._validation_message)
            return False
            
        return True

    def is_valid(self) -> bool:
        """
        Validate field content.
        
        Returns:
            bool: True if field content is valid, False otherwise
        """
        value = self.get_value()
        
        # Custom pattern validation
        if not self._validate_pattern(value):
            return False
        
        # Validate based on filter type
        is_valid = True
        if self._input_filter == InputFilter.EMAIL:
            is_valid = self._validate_email(value)
        elif self._input_filter == InputFilter.NUMERIC:
            is_valid = self._validate_numeric(value)
        elif self._input_filter == InputFilter.TEXT:
            if not self._validate_text_length(value):
                return False
        
        # Required field validation
        if self._required and not value:
            self.show_error(self._error_messages["required"])
            is_valid = False
        elif is_valid:
            self.hide_error()
            
        return is_valid
        
    def get_value(self) -> str:
        """Get current field value."""
        return self.line_edit.text().strip()

    def set_value(self, value: str) -> None:
        """Set field value."""
        self.line_edit.setText(str(value))

    def clear_content(self) -> None:
        """Clear field content."""
        super().clear_content()
        self.line_edit.clear()
        
        
class TextField(TextFieldBase):
    """
    Standard text input field.
    
    Args:
        key (str, optional): Unique widget identifier
        width (int, optional): Widget width in pixels
        height (int, optional): Widget height in pixels
        tooltip (str, optional): Hover tooltip text
        visible (bool): Initial visibility state
        disabled (bool): Initial disabled state
        theme (TextFieldTheme): Field theme configuration
        label (str, optional): Label text
        hint_text (str, optional): Placeholder text
        helper_text (str, optional): Helper text below field
        error_messages (Dict[str, str], optional): Custom error messages
        required (bool): Whether field is required
        value (str, optional): Initial value
        read_only (bool): Read-only mode
        min_length (Optional[int]): Minimum text length
        max_length (Optional[int]): Maximum text length
        validation_pattern (Optional[str]): Regex pattern for custom validation
        validation_message (Optional[str]): Error message for pattern validation
        on_change (Callable, optional): Value change callback
        on_focus (Callable, optional): Focus gained callback
        on_blur (Callable, optional): Focus lost callback
        parent (QWidget, optional): Parent widget
    
    Examples:
        >>> # Champ texte simple
        >>> text_field = TextField(label="Nom", required=True)
        
        >>> # Champ texte avec validation de longueur
        >>> description = TextField(
        ...     label="Description",
        ...     min_length=10,
        ...     max_length=200,
        ...     hint_text="Minimum 10 caractères"
        ... )
        
        >>> # Champ texte avec pattern personnalisé
        >>> username = TextField(
        ...     label="Nom d'utilisateur",
        ...     validation_pattern=r"^[a-zA-Z0-9_]+$",
        ...     validation_message="Uniquement lettres, chiffres et underscore"
        ... )
    """
    def __init__(
        self,
        key: Optional[str] = None,
        width: Optional[int] = 300,
        height: Optional[int] = 40,
        tooltip: Optional[str] = None,
        visible: bool = True,
        disabled: bool = False,
        theme: TextFieldTheme = ThemeManager.TextFieldThemes.DEFAULT,
        label: Optional[str] = None,
        hint_text: Optional[str] = None,
        helper_text: Optional[str] = None,
        error_messages: Optional[Dict[str, str]] = None,
        required: bool = False,
        value: Optional[str] = None,
        read_only: bool = False,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        validation_pattern: Optional[str] = None,
        validation_message: Optional[str] = None,
        on_change: Optional[Callable] = None,
        on_focus: Optional[Callable] = None,
        on_blur: Optional[Callable] = None,
        parent = None,
    ) -> None:
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
            error_messages=error_messages,
            required=required,
            value=value,
            password=False,
            can_reveal_password=False,
            read_only=read_only,
            input_filter=InputFilter.TEXT,
            min_length=min_length,
            max_length=max_length,
            validation_pattern=validation_pattern,
            validation_message=validation_message,
            on_change=on_change,
            on_focus=on_focus,
            on_blur=on_blur,
            parent=parent
        )

class EmailField(TextFieldBase):
    """
    Email input field with email format validation.
    
    Args:
        key (str, optional): Unique widget identifier
        width (int, optional): Widget width in pixels
        height (int, optional): Widget height in pixels
        tooltip (str, optional): Hover tooltip text
        visible (bool): Initial visibility state
        disabled (bool): Initial disabled state
        theme (TextFieldTheme): Field theme configuration
        label (str, optional): Label text
        hint_text (str, optional): Placeholder text
        helper_text (str, optional): Helper text below field
        error_messages (Dict[str, str], optional): Custom error messages
        required (bool): Whether field is required
        value (str, optional): Initial value
        read_only (bool): Read-only mode
        validation_pattern (Optional[str]): Additional regex pattern for validation
        validation_message (Optional[str]): Error message for pattern validation
        on_change (Callable, optional): Value change callback
        on_focus (Callable, optional): Focus gained callback
        on_blur (Callable, optional): Focus lost callback
        parent (QWidget, optional): Parent widget
    
    Examples:
        >>> # Email field simple
        >>> email = EmailField(
        ...     label="Email",
        ...     hint_text="exemple@domaine.com",
        ...     required=True
        ... )
        
        >>> # Email field avec validation supplémentaire
        >>> email_pro = EmailField(
        ...     label="Email professionnel",
        ...     validation_pattern=r"^[a-zA-Z0-9_.+-]+@entreprise\.com$",
        ...     validation_message="Utilisez votre email @entreprise.com"
        ... )
    """

    def __init__(
        self,
        key: Optional[str] = None,
        width: Optional[int] = 300,
        height: Optional[int] = 40,
        tooltip: Optional[str] = None,
        visible: bool = True,
        disabled: bool = False,
        theme: TextFieldTheme = ThemeManager.TextFieldThemes.DEFAULT,
        label: Optional[str] = None,
        hint_text: Optional[str] = None,
        helper_text: Optional[str] = None,
        error_messages: Optional[Dict[str, str]] = None,
        required: bool = False,
        value: Optional[str] = None,
        read_only: bool = False,
        validation_pattern: Optional[str] = None,
        validation_message: Optional[str] = None,
        on_change: Optional[Callable] = None,
        on_focus: Optional[Callable] = None,
        on_blur: Optional[Callable] = None,
        parent = None,
    ) -> None:
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
            error_messages=error_messages,
            required=required,
            value=value,
            password=False,
            can_reveal_password=False,
            read_only=read_only,
            input_filter=InputFilter.EMAIL,
            validation_pattern=validation_pattern,
            validation_message=validation_message,
            on_change=on_change,
            on_focus=on_focus,
            on_blur=on_blur,
            parent=parent
        )

class PasswordField(TextFieldBase):
    """
    Password input field with masked input and optional reveal button.
    
    Args:
        key (str, optional): Unique widget identifier
        width (int, optional): Widget width in pixels
        height (int, optional): Widget height in pixels
        tooltip (str, optional): Hover tooltip text
        visible (bool): Initial visibility state
        disabled (bool): Initial disabled state
        theme (TextFieldTheme): Field theme configuration
        label (str, optional): Label text
        hint_text (str, optional): Placeholder text
        helper_text (str, optional): Helper text below field
        error_messages (Dict[str, str], optional): Custom error messages
        required (bool): Whether field is required
        value (str, optional): Initial value
        can_reveal_password (bool): Allow password visibility toggle
        read_only (bool): Read-only mode
        min_length (Optional[int]): Minimum password length
        max_length (Optional[int]): Maximum password length
        validation_pattern (Optional[str]): Regex pattern for password rules
        validation_message (Optional[str]): Error message for pattern validation
        on_change (Callable, optional): Value change callback
        on_focus (Callable, optional): Focus gained callback
        on_blur (Callable, optional): Focus lost callback
        parent (QWidget, optional): Parent widget
    
    Examples:
        >>> # Champ mot de passe simple
        >>> password = PasswordField(
        ...     label="Mot de passe",
        ...     required=True,
        ...     can_reveal_password=True
        ... )
        
        >>> # Mot de passe avec règles de complexité
        >>> password_secure = PasswordField(
        ...     label="Mot de passe",
        ...     min_length=8,
        ...     validation_pattern=r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])",
        ...     validation_message="8 caractères min., majuscule, minuscule, chiffre et caractère spécial"
        ... )
    """

    def __init__(
        self,
        key: Optional[str] = None,
        width: Optional[int] = 300,
        height: Optional[int] = 40,
        tooltip: Optional[str] = None,
        visible: bool = True,
        disabled: bool = False,
        theme: TextFieldTheme = ThemeManager.TextFieldThemes.DEFAULT,
        label: Optional[str] = None,
        hint_text: Optional[str] = None,
        helper_text: Optional[str] = None,
        error_messages: Optional[Dict[str, str]] = None,
        required: bool = False,
        value: Optional[str] = None,
        can_reveal_password: bool = False,
        read_only: bool = False,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        validation_pattern: Optional[str] = None,
        validation_message: Optional[str] = None,
        on_change: Optional[Callable] = None,
        on_focus: Optional[Callable] = None,
        on_blur: Optional[Callable] = None,
        parent = None,
    ) -> None:
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
            error_messages=error_messages,
            required=required,
            value=value,
            password=True,
            can_reveal_password=can_reveal_password,
            read_only=read_only,
            input_filter=InputFilter.TEXT,
            min_length=min_length,
            max_length=max_length,
            validation_pattern=validation_pattern,
            validation_message=validation_message,
            on_change=on_change,
            on_focus=on_focus,
            on_blur=on_blur,
            parent=parent
        )

class NumberField(TextFieldBase):
    """
    Numeric input field with number format and range validation.
    
    Args:
        key (str, optional): Unique widget identifier
        width (int, optional): Widget width in pixels
        height (int, optional): Widget height in pixels
        tooltip (str, optional): Hover tooltip text
        visible (bool): Initial visibility state
        disabled (bool): Initial disabled state
        theme (TextFieldTheme): Field theme configuration
        label (str, optional): Label text
        hint_text (str, optional): Placeholder text
        helper_text (str, optional): Helper text below field
        error_messages (Dict[str, str], optional): Custom error messages
        required (bool): Whether field is required
        value (str, optional): Initial value
        min_value (Optional[float]): Minimum allowed value
        max_value (Optional[float]): Maximum allowed value
        read_only (bool): Read-only mode
        validation_pattern (Optional[str]): Additional regex pattern for validation
        validation_message (Optional[str]): Error message for pattern validation
        on_change (Callable, optional): Value change callback
        on_focus (Callable, optional): Focus gained callback
        on_blur (Callable, optional): Focus lost callback
        parent (QWidget, optional): Parent widget
    
    Examples:
        >>> # Champ numérique simple
        >>> age = NumberField(
        ...     label="Âge",
        ...     min_value=0,
        ...     max_value=120
        ... )
        
        >>> # Champ pour note avec décimales
        >>> note = NumberField(
        ...     label="Note",
        ...     min_value=0,
        ...     max_value=20,
        ...     validation_pattern=r"^\d+(\.\d{1,2})?$",
        ...     validation_message="Format: XX.XX"
        ... )
        
        >>> # Champ pour montant avec validation
        >>> montant = NumberField(
        ...     label="Montant",
        ...     min_value=0,
        ...     validation_pattern=r"^\d+(\.\d{2})?$",
        ...     validation_message="Format: XX.XX €"
        ... )
    """

    def __init__(
        self,
        key: Optional[str] = None,
        width: Optional[int] = 300,
        height: Optional[int] = 40,
        tooltip: Optional[str] = None,
        visible: bool = True,
        disabled: bool = False,
        theme: TextFieldTheme = ThemeManager.TextFieldThemes.DEFAULT,
        label: Optional[str] = None,
        hint_text: Optional[str] = None,
        helper_text: Optional[str] = None,
        error_messages: Optional[Dict[str, str]] = None,
        required: bool = False,
        value: Optional[str] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        read_only: bool = False,
        validation_pattern: Optional[str] = None,
        validation_message: Optional[str] = None,
        on_change: Optional[Callable] = None,
        on_focus: Optional[Callable] = None,
        on_blur: Optional[Callable] = None,
        parent = None,
    ) -> None:
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
            error_messages=error_messages,
            required=required,
            value=value,
            password=False,
            can_reveal_password=False,
            min_value=min_value,
            max_value=max_value,
            read_only=read_only,
            input_filter=InputFilter.NUMERIC,
            validation_pattern=validation_pattern,
            validation_message=validation_message,
            on_change=on_change,
            on_focus=on_focus,
            on_blur=on_blur,
            parent=parent
        )