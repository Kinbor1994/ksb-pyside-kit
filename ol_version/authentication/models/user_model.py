from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum
import enum
from ...components.widget_types import WidgetType
from ...models import BaseModel

class UserType(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    SUPERUSER = "superuser"
    DEFAULT = "user"

class UserModel(BaseModel):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    __verbose_name__ = "Utilisateur"

    username = Column(
        String(50), 
        unique=True,
        nullable=False,
        index=True,
        info={
            "verbose_name": "Nom d'utilisateur",
            "widget_type": WidgetType.TEXT,
            "tab_col_index": 1,
            "filterable": True,
        }
    )
    email = Column(
        String(100),
        unique=True,
        nullable=False,
        info={
            "verbose_name": "Email",
            "widget_type": WidgetType.EMAIL,
            "tab_col_index": 2,
        }
    )
    password = Column(
        String(255),
        nullable=False,
        info={
            "verbose_name": "Mot de passe",
            "widget_type": WidgetType.PASSWORD,
            "tab_col_index": 3,
        }
    )
    first_name = Column(
        String(50),
        nullable=True,
        info={
            "verbose_name": "Prénom",
            "widget_type": WidgetType.TEXT,
            "tab_col_index": 4,
        }
    )
    last_name = Column(
        String(50),
        nullable=True,
        info={
            "verbose_name": "Nom",
            "widget_type": WidgetType.TEXT,
            "tab_col_index": 5,
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
            "tab_col_index": 6,
            "filterable": True,
        }
    )
    is_active = Column(
        Boolean,
        default=True,
        info={
            "verbose_name": "Actif",
            "widget_type": WidgetType.COMBOBOX,
            "tab_col_index": 7,
        }
    )
    secret_question = Column(
        String(255),
        nullable=False,
        info={
            "verbose_name": "Question secrète",
            "widget_type": WidgetType.COMBOBOX,
            "choices": [
                ("Quel est le nom de votre premier animal de compagnie ?", "Quel est le nom de votre premier animal de compagnie ?"),
                ("Dans quelle ville êtes-vous né(e) ?", "Dans quelle ville êtes-vous né(e) ?"),
                ("Quel est le nom de jeune fille de votre mère ?", "Quel est le nom de jeune fille de votre mère ?"),
                ("Quel est votre film préféré ?", "Quel est votre film préféré ?"),
                ("Quel est le nom de votre meilleur ami ?", "Quel est le nom de votre meilleur ami ?"),
                ("Quel est le nom de votre école primaire ?", "Quel est le nom de votre école primaire ?"),
                ("Quel est votre plat préféré ?", "Quel est votre plat préféré ?"),
                ("Quel est le nom de votre héros d'enfance ?", "Quel est le nom de votre héros d'enfance ?"),
            ],
            "tab_col_index": 8,
        }
    )
    secret_answer = Column(
        String(255),
        nullable=False,
        info={
            "verbose_name": "Réponse secrète",
            "widget_type": WidgetType.TEXT,
            "tab_col_index": 9,
        }
    )
    last_login = Column(
        DateTime,
        nullable=True,
        info={
            "verbose_name": "Dernière connexion",
            "widget_type": WidgetType.DATETIME,
            "tab_col_index": 10,
        }
    )
    date_joined = Column(
        DateTime,
        default=datetime.now,
        nullable=False,
        info={
            "verbose_name": "Date d'inscription",
            "widget_type": WidgetType.DATETIME,
            "tab_col_index": 11,
        }
    )

    def __str__(self):
        """Return a string representation of the user"""
        return self.username