from typing import Any, Optional, Type, TypeVar, Dict
from sqlalchemy.orm import DeclarativeBase
from PySide6.QtCore import Signal

from ..widgets.combobox import ComboBox
from ..core.themes.themes import ThemeManager, FormTheme
from ..controllers.base_controller import BaseController
from .base import FormBase, FormModalBase
from ..core.exceptions import ValidationError
from ..models.metadata import ColumnMetadata
from ..components.message_box import MessageBox, MessageBoxResult


ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class FormMode:
    """Available form modes"""
    CREATE = "create"
    UPDATE = "update" 
    VIEW = "view"


class FormModel(FormBase):
    """
    A dynamic form class generated from a SQLAlchemy model.
    
    This class automatically creates form fields based on the metadata 
    defined in each column's .info attribute. It supports CRUD operations 
    using a provided controller.
    """
    
    # Signals
    submitted = Signal(dict)  # Emitted after successful save
    validation_failed = Signal(dict)  # Emitted on validation errors
    
    def __init__(
        self,
        model_class: Type[DeclarativeBase],
        controller: BaseController,
        instance: Optional[DeclarativeBase] = None,
        mode: str = FormMode.CREATE,
        title: Optional[str] = None,
        parent: Optional[Any] = None,
        show_buttons: bool = True,
        submit_text: str = "Enregistrer",
        cancel_text: str = "Annuler",
        theme: Optional[FormTheme] = ThemeManager.FormThemes.DEFAULT,
    ):
        """Initialize a new form instance."""
        self.model_class = model_class
        self.controller = controller
        self.instance = instance
        self.mode = mode
        self._errors: Dict[str, list] = {}

        # Set default title if not provided
        if not title and hasattr(model_class, "__verbose_name__"):
            action = "Modification" if instance else "Création"
            title = f"{action} de {model_class.__verbose_name__}"

        super().__init__(
            title=title,
            parent=parent,
            show_buttons=show_buttons,
            submit_text=submit_text,
            cancel_text=cancel_text,
            theme=theme
        )

        self._init_ui()
        
    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self._auto_generate_form_fields()
        if self.instance:
            self._populate_from_instance()

    def _auto_generate_form_fields(self) -> None:
        """
        Generate form fields based on model columns.
        
        Only generates fields that:
        - Have ColumnMetadata in their .info
        - Are visible
        - Are editable (unless in VIEW mode)
        - Have a form_field_type defined
        """
        for column in self.model_class.__table__.columns:
            if not isinstance(column.info, ColumnMetadata):
                continue
            
            metadata = column.info
                
            # Skip non-editable fields in CREATE/UPDATE mode
            if self.mode != FormMode.VIEW and not metadata.editable:
                continue

            # Create and add field if form_field_type is defined
            if field := metadata.form_field:
                # Handle foreign key fields
                if column.foreign_keys and isinstance(field, ComboBox):
                    self._setup_foreign_key_field(column, field)
                    
                # In VIEW mode, all fields should be disabled
                if self.mode == FormMode.VIEW:
                    field.setEnabled(False)
                
                # Add field to form at specified position
                if metadata.form_position:
                    self.add_field(field, metadata.form_position)

    def _populate_from_instance(self) -> None:
        """
        Fill the form with data from an existing record.
        
        Only populates visible fields that have corresponding form widgets.
        """
        if not self.instance:
            return
        
        columns = self.model_class.__table__.columns
        for column in columns:
            if not isinstance(column.info, ColumnMetadata):
                continue
                
            metadata = column.info
            if not metadata.visible:
                continue
                
            value = getattr(self.instance, column.key, None)
            if field := self._fields.get(column.key):
                field.set_value(value)

    def _handle_submit(self) -> None:
        """Handle form submission and database operations."""
        super()._handle_submit()
        
        if not self._is_valid():
            self.validation_failed.emit(self._errors)
            MessageBox.show_error(
                title="Erreur",
                message="Veuillez corriger les erreurs.",
                parent=self
            )
            return

        try:
            data = self.get_data()

            if self.instance:
                # Update existing record
                updated = self.controller.update(self.instance.id, **data)
                self.submitted.emit(updated.to_dict())
                self.close()
                MessageBox.show_info(
                    title="Succès",
                    message="Mise à jour effectuée avec succès.",
                    parent=self
                )
            else:
                # Create new record
                created = self.controller.create(**data)
                self.submitted.emit(created.to_dict())
                MessageBox.show_info(
                    title="Succès",
                    message="Enregistrement effetué avec succès.",
                    parent=self
                )
                
            self.clear()

        except ValidationError as e:
            self._errors["__form__"] = [str(e)]
            self.validation_failed.emit(self._errors)
            MessageBox.show_error(
                title="Erreur de validation",
                message=str(e),
                parent=self
            )
        except Exception as e:
            self._errors["__form__"] = [f"Une erreur inattendue s'est produite: {str(e)}"]
            print(str(e))
            self.validation_failed.emit(self._errors)
            MessageBox.show_error(
                title="Erreur inattendue",
                message=f"Une erreur inattendue s'est produite: {str(e)}",
                parent=self
            )
            
    def _handle_cancel(self):
        super()._handle_cancel()
        self.close()
        
    def _setup_foreign_key_field(self, column, field: ComboBox) -> None:
        """
        Setup a ComboBox field for a foreign key relationship.
        
        Args:
            column: The SQLAlchemy Column with foreign key
            field: The ComboBox widget to setup
        """
        try:

            # Load related items using controller
            related_items = self.controller.get_related_model_items(column.name)
            
            if related_items:
                # Convert items to options format (value, label)
                options=[(str(item), item.id) for item in related_items]
    
                # Set options on field
                field.set_options(options)
                
        except Exception as e:
            print(f"Error loading options for {column.name}: {str(e)}")
        
class FormModelModal(FormModalBase):
    """
    A dynamic form class generated from a SQLAlchemy model.
    
    This class automatically creates form fields based on the metadata 
    defined in each column's .info attribute. It supports CRUD operations 
    using a provided controller.
    """
    
    # Signals
    submitted = Signal(dict)  # Emitted after successful save
    validation_failed = Signal(dict)  # Emitted on validation errors
    
    def __init__(
        self,
        model_class: Type[DeclarativeBase],
        controller: BaseController,
        instance: Optional[DeclarativeBase] = None,
        mode: str = FormMode.CREATE,
        title: Optional[str] = None,
        parent: Optional[Any] = None,
        show_buttons: bool = True,
        submit_text: str = "Enregistrer",
        cancel_text: str = "Annuler",
        theme: Optional[FormTheme] = ThemeManager.FormThemes.DEFAULT,
    ):
        """Initialize a new form instance."""
        self.model_class = model_class
        self.controller = controller
        self.instance = instance
        self.mode = mode
        self._errors: Dict[str, list] = {}

        # Set default title if not provided
        if not title and hasattr(model_class, "__verbose_name__"):
            action = "Modification" if instance else "Création"
            title = f"{action} de {model_class.__verbose_name__}"

        super().__init__(
            title=title,
            parent=parent,
            show_buttons=show_buttons,
            submit_text=submit_text,
            cancel_text=cancel_text,
            theme=theme
        )

        self._init_ui()
        
    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self._auto_generate_form_fields()
        if self.instance:
            self._populate_from_instance()

    def _auto_generate_form_fields(self) -> None:
        """
        Generate form fields based on model columns.
        
        Only generates fields that:
        - Have ColumnMetadata in their .info
        - Are visible
        - Are editable (unless in VIEW mode)
        - Have a form_field_type defined
        """
        for column in self.model_class.__table__.columns:
            if not isinstance(column.info, ColumnMetadata):
                continue
            
            metadata = column.info
                
            # Skip non-editable fields in CREATE/UPDATE mode
            if self.mode != FormMode.VIEW and not metadata.editable:
                continue

            # Create and add field if form_field_type is defined
            if field := metadata.form_field:
                # Handle foreign key fields
                if column.foreign_keys and isinstance(field, ComboBox):
                    self._setup_foreign_key_field(column, field)
                    
                # In VIEW mode, all fields should be disabled
                if self.mode == FormMode.VIEW:
                    field.setEnabled(False)
                
                # Add field to form at specified position
                if metadata.form_position:
                    self.add_field(field, metadata.form_position)

    def _populate_from_instance(self) -> None:
        """
        Fill the form with data from an existing record.
        
        Only populates visible fields that have corresponding form widgets.
        """
        if not self.instance:
            return
        
        columns = self.model_class.__table__.columns
        for column in columns:
            if not isinstance(column.info, ColumnMetadata):
                continue
                
            metadata = column.info
            if not metadata.common_attributes.get("visible", True):
                continue
                
            value = getattr(self.instance, column.key, None)
            if field := self._fields.get(column.key):
                field.set_value(value)

    def _handle_submit(self) -> None:
        """Handle form submission and database operations."""
        super()._handle_submit()
        
        if not self._is_valid():
            self.validation_failed.emit(self._errors)
            MessageBox.show_error(
                title="Erreur",
                message="Veuillez corriger les erreurs.",
                parent=self
            )
            return

        try:
            data = self.get_data()

            if self.instance:
                # Update existing record
                updated = self.controller.update(self.instance.id, **data)
                self.submitted.emit(updated.to_dict())
                MessageBox.show_info(
                    title="Succès",
                    message="Mise à jour effectuée avec succès.",
                    parent=self
                )
                self.close()
            else:
                # Create new record
                created = self.controller.create(**data)
                self.submitted.emit(created.to_dict())
                MessageBox.show_info(
                    title="Succès",
                    message="Enregistrement effectué avec succès.",
                    parent=self
                )
                
            self.clear()

        except ValidationError as e:
            self._errors["__form__"] = [str(e)]
            self.validation_failed.emit(self._errors)
            MessageBox.show_error(
                title="Erreur de validation",
                message=str(e),
                parent=self
            )
        except Exception as e:
            self._errors["__form__"] = [f"Une erreur inattendue s'est produite: {str(e)}"]
            self.validation_failed.emit(self._errors)
            MessageBox.show_error(
                title="Erreur inattendue",
                message=f"Une erreur inattendue s'est produite: {str(e)}",
                parent=self
            )
            
    def _handle_cancel(self):
        super()._handle_cancel()
        self.close()
        
    def _setup_foreign_key_field(self, column, field: ComboBox) -> None:
        """
        Setup a ComboBox field for a foreign key relationship.
        
        Args:
            column: The SQLAlchemy Column with foreign key
            field: The ComboBox widget to setup
        """
        try:

            # Load related items using controller
            related_items = self.controller.get_related_model_items(column.name)
            
            if related_items:
                # Convert items to options format (value, label)
                options=[(str(item), item.id) for item in related_items]
    
                # Set options on field
                field.set_options(options)
                
        except Exception as e:
            print(f"Error loading options for {column.name}: {str(e)}")
        
