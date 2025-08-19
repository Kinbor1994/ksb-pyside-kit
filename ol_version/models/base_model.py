from typing import Any, Dict
from sqlalchemy import Column, Integer, DateTime, func
from database.database import Base
from ..widgets import NumberField, DateField
from .metadata import ColumnMetadata

class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        info=ColumnMetadata(
            form_field_type=NumberField,
            key="id",
            label="ID",
            visible=False,
            required=False,
            editable=False,
            grid_column_index=1,
        )
    )

    created_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        info=ColumnMetadata(
            form_field_type=DateField,
            key="created_at",
            label="Date de création",
            visible=False,
            editable=False,
            grid_column_index=-2,
            tooltip="Date de création de l'enregistrement",
        )
    )

    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        info=ColumnMetadata(
            form_field_type=DateField,
            key="updated_at", 
            label="Dernière modification",
            visible=False,
            editable=False,
            grid_column_index=-1,
            tooltip="Date de dernière modification",
        )
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        Only includes columns with visible metadata.
        """
        data = {}
        for column in self.__table__.columns:
            if not isinstance(column.info, ColumnMetadata):
                continue
                
            metadata = column.info
            if not metadata.common_attributes.get("visible", True):
                continue
                
            value = getattr(self, column.key, None)
            data[column.key] = value
            
        return data