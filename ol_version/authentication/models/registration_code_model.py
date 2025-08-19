from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Enum
from ...models import BaseModel
from .user_model import UserType
from ...components.widget_types import WidgetType

class RegistrationCodeModel(BaseModel):
    """Model for registration codes"""
    __tablename__ = "registration_codes"
    __verbose_name__ = "Code d'inscription"
    
    code = Column(
        String(20),
        unique=True,
        nullable=False,
        info={
            "verbose_name": "Code",
            "widget_type": WidgetType.TEXT,
            "filterable": True,
        }
    )
    
    user_type = Column(
        Enum(UserType),
        default=UserType.DEFAULT,
        nullable=False,
        info={
            "verbose_name": "Type d'utilisateur",
            "widget_type": WidgetType.COMBOBOX,
            "choices": [(t.value, t.value) for t in UserType],
            "filterable": True,
        }
    )
    
    is_used = Column(
        Boolean,
        default=False,
        info={
            "verbose_name": "Utilisé",
            "widget_type": WidgetType.COMBOBOX,
        }
    )
    
    expiration_date = Column(
        DateTime,
        nullable=False,
        info={
            "verbose_name": "Date d'expiration",
            "widget_type": WidgetType.DATETIME,
        }
    )
