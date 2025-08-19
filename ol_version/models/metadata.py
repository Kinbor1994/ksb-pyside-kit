from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Union, Tuple, Type
from ..core.base_form_field import BaseFormField
from ..forms.base import FieldPosition
from ..core.themes.themes import ThemeManager

@dataclass
class ColumnMetadata:
    """Helper class to create column metadata for form and grid generation."""
    
    def __init__(
        self,
        form_field_type: Optional[Type[BaseFormField]] = None,
        form_position: Optional[Union[FieldPosition, Tuple[int, int]]] = None,
        grid_column_index: Optional[int] = None,
        editable: bool = True,
        sortable: bool = False,
        filterable: bool = False,
        filter_type: Optional[Type[BaseFormField]] = None,
        related_info: Optional[Dict[str, Any]] = None,
        
        # Common form field attributes
        key: Optional[str] = None,
        tooltip: Optional[str] = None,
        visible: bool = True,
        label: Optional[str] = None,
        #hint_text: Optional[str] = None,
        helper_text: Optional[str] = None,
        error_messages: Optional[Dict[str, str]] = None,
        required: bool = False,
        on_change: Optional[Callable] = None,
        on_focus: Optional[Callable] = None,
        on_blur: Optional[Callable] = None,
        
        # Field specific attributes
        field_attributes: Optional[Dict[str, Any]] = None,
    ):
        # Column metadata attributes
        self.form_field_type = form_field_type
        self.grid_column_index = grid_column_index
        self.editable = editable
        self.sortable = sortable
        self.filterable = filterable
        self.filter_type = filter_type
        self.related_info = related_info
        
        # Common form field attributes
        self.common_attributes = {
            "key": key or "",
            "label": label,
            "required": required,
            "tooltip": tooltip,
            "helper_text": helper_text,
            "visible": visible,
            "disabled": not self.editable,
            "on_change": on_change,
            "on_focus": on_focus,
            "on_blur": on_blur,
            "error_messages": error_messages or {},
        }
        
        # Field specific attributes (e.g. for ComboBox, FileField, etc.)
        self.field_attributes = field_attributes or {}

        # Handle form position
        if isinstance(form_position, tuple):
            self.form_position = FieldPosition(row=form_position[0], column=form_position[1])
        else:
            self.form_position = form_position

    def copy(self):
        """Create a deep copy of the metadata"""
        return deepcopy(self)

    def _schema_item_copy(self):
        """SQLAlchemy compatibility method"""
        return self.copy()
    
    @property
    def form_field(self) -> Optional[BaseFormField]:
        """Create form field instance with configured attributes"""
        if self.form_field_type is None:
            return None
            
        # Combine all attributes
        field_attrs = {}
        field_attrs.update(self.common_attributes)
        field_attrs.update(self.field_attributes)
        
        return self.form_field_type(**field_attrs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary format"""
        metadata = {
            "form_field": self.form_field,
            "grid_column_index": self.grid_column_index,
            "editable": self.editable,
            "sortable": self.sortable,
            "form_position": self.form_position,
            "related_info": self.related_info,
            "field_attributes": self.field_attributes
        }
        
        return {k: v for k, v in metadata.items() if v is not None}