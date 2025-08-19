from typing import Dict, Any, Optional, List, Callable, ClassVar, Tuple

from ..core.commons import QWidget
from .base import FormBase, FieldPosition, FormModalBase
from ..core.base_form_field import BaseFormField
from ..core.exceptions import ValidationError
from ..core.themes.themes import ThemeManager, FormTheme

class Form(FormBase[BaseFormField]):
    """
    Form class with declarative field definitions and grid positioning.
    """

    class Meta:
        fields: ClassVar[Dict[str, Tuple[BaseFormField, Optional[FieldPosition]]]] = {}
        validators: List[Callable] = []

    def __init__(
        self,
        title: Optional[str] = None,
        parent: Optional[QWidget] = None,
        show_buttons: bool = True,
        submit_text: str = "Enregistrer",
        cancel_text: str = "Annuler",
        theme: Optional[FormTheme] = ThemeManager.FormThemes.DEFAULT
    ) -> None:
        super().__init__(
            title=title,
            parent=parent,
            show_buttons=show_buttons,
            submit_text=submit_text,
            cancel_text=cancel_text,
            theme=theme
        )
        self._initialize_from_meta()

    def _initialize_from_meta(self) -> None:
        """
        Initialize form fields and validators from Meta class.
        Fields can now be positioned using FieldPosition.
        """
        meta = getattr(self, 'Meta', None)
        if not meta:
            return

        # Add fields with their positions from Meta
        for field_name, field_data in meta.fields.items():
            if isinstance(field_data, tuple) and len(field_data) == 2:
                field, position = field_data
            else:
                field = field_data
                position = None
                
            self.add_field(field, position)

        # Add form validators
        if hasattr(meta, 'validators'):
            for validator in meta.validators:
                self.add_validator(validator)
                
                
class FormModal(FormModalBase[BaseFormField]):
    """
    Form class with declarative field definitions and grid positioning.
    """

    class Meta:
        fields: ClassVar[Dict[str, Tuple[BaseFormField, Optional[FieldPosition]]]] = {}
        validators: List[Callable] = []

    def __init__(
        self,
        title: Optional[str] = None,
        parent: Optional[QWidget] = None,
        show_buttons: bool = True,
        submit_text: str = "Enregistrer",
        cancel_text: str = "Annuler",
        theme: Optional[FormTheme] = ThemeManager.FormThemes.DEFAULT
    ) -> None:
        super().__init__(
            title=title,
            parent=parent,
            show_buttons=show_buttons,
            submit_text=submit_text,
            cancel_text=cancel_text,
            theme=theme
        )
        self._initialize_from_meta()

    def _initialize_from_meta(self) -> None:
        """
        Initialize form fields and validators from Meta class.
        Fields can now be positioned using FieldPosition.
        """
        meta = getattr(self, 'Meta', None)
        if not meta:
            return

        # Add fields with their positions from Meta
        for field_name, field_data in meta.fields.items():
            if isinstance(field_data, tuple) and len(field_data) == 2:
                field, position = field_data
            else:
                field = field_data
                position = None
                
            self.add_field(field, position)

        # Add form validators
        if hasattr(meta, 'validators'):
            for validator in meta.validators:
                self.add_validator(validator)