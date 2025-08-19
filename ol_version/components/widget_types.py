from enum import Enum


class WidgetType(Enum):
    TEXT = "text"
    NUMBER = "number"
    EMAIL = "email"
    PASSWORD = "password"
    DATE = "date"
    DATETIME = "datetime"
    COMBOBOX = "combobox"
    TEXTAREA = "textarea"
    PHONE = "phone"
    FILE = "file"
    