"""Centralized theme management for PySide6 widgets with dynamic Inter font loading.

This module provides a unified theming system for PySide6 widgets, ensuring
consistency across the application with the Inter font (static variants) and a
Bootstrap-inspired color palette. It includes dynamic loading of Inter fonts using
QFontDatabase with pathlib for path handling.
"""

from dataclasses import dataclass
from typing import Optional, Union, Tuple
from ..commons import QMessageBox, QApplication, QFontDatabase
import logging

from ksb_pyside_kit.settings import FONT_DIR
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThemeConstants:
    """Global constants for theming consistency."""

    # Font configuration
    FONT_FAMILY = '"Open Sans", "Segoe UI Variable", "Segoe UI",Roboto, sans-serif'
    FONT_SIZES = {
        "small": 12,
        "default": 14,
        "large": 16,
        "heading": 20,
        "display": 28,
        "h1": 40,
        "h2": 32,
        "h3": 28,
        "h4": 24,
        "h5": 20,
        "h6": 16,
        "lead": 20,
        "badge": 12,
        "logo": 27,
    }

    # Colors (Bootstrap-inspired)
    COLORS = {
        "primary": "#0d6efd",
        "secondary": "#6c757d",
        "success": "#198754",
        "danger": "#dc3545",
        "warning": "#ffc107",
        "info": "#0dcaf0",
        "light": "#f8f9fa",
        "dark": "#212529",
        "white": "#ffffff",
        "muted": "#6c757d",
        "primary-dark": "#0056b3",
        "light-dark": "#e2e6ea",
        "dark-light": "#343a40",
        "card-title": "#313131",
        "card-value": "#252422",
        "card-footer": "#313131",
        "table-hover": "#e9ecef",  
        "table-border": "#dee2e6",  
    }

    # Spacing and dimensions
    BORDER_RADIUS = {"small": 5, "medium": 12, "large": 15, "table": 4}
    PADDING = {
        "default": (0, 0, 0, 0),
        "small": (3, 6, 3, 6),
        "medium": (6, 12, 6, 12),
        "large": (8, 15, 8, 15),
        "badge": (3, 6, 3, 6),
        "table-cell": (8, 12, 8, 12),
    }
    HEIGHT = {"default": 40, "small": 32, "large": 48}


class FontLoader:
    """Utility class to load Inter Variable font using QFontDatabase with pathlib."""

    # Inter Variable contient toutes les épaisseurs en un seul fichier
    FONT_PATHS = {
        "regular": FONT_DIR / "OpenSans-Regular.ttf",
        "medium": FONT_DIR / "OpenSans-Medium.ttf",
        "semibold": FONT_DIR / "OpenSans-SemiBold.ttf",
        "bold": FONT_DIR / "OpenSans-Bold.ttf",
        "italic": FONT_DIR / "OpenSans-Italic.ttf",
    }

    _instance = None
    _fonts_loaded = False
    _missing_fonts = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FontLoader, cls).__new__(cls)
            # Tentative de chargement automatique lors de la première instanciation
            cls._try_load_fonts()
        return cls._instance

    @classmethod
    def _try_load_fonts(cls):
        """Tente de charger les polices s'il existe une instance de QApplication."""
        if QApplication.instance() is not None and not cls._fonts_loaded:
            cls.load_fonts(show_warnings=False)

    @classmethod
    def load_fonts(cls, show_warnings=False) -> bool:
        """Load Inter Variable font into the application."""
        # Si l'application n'est pas initialisée, on ne peut pas charger les polices
        if QApplication.instance() is None:
            logger.debug(
                "QApplication n'est pas encore initialisée. Les polices seront chargées plus tard."
            )
            return False

        # If fonts are already loaded, return the previous result
        if cls._fonts_loaded:
            return len(cls._missing_fonts) == 0

        font_db = QFontDatabase()
        success = True
        cls._missing_fonts = []

        for font_name, font_path in cls.FONT_PATHS.items():
            if not font_path.exists():
                logger.error(f"Fichier de police manquant : {font_path}")
                cls._missing_fonts.append(str(font_path))
                success = False
                continue

            font_id = font_db.addApplicationFont(str(font_path))
            if font_id == -1:
                logger.error(f"Échec du chargement de la police : {font_path}")
                cls._missing_fonts.append(str(font_path))
                success = False
            else:
                loaded_fonts = font_db.applicationFontFamilies(font_id)
                logger.info(f"Police chargée : {loaded_fonts} depuis {font_path}")

        if not success:
            logger.warning(
                "La police Inter Variable n'a pas pu être chargée. L'application utilisera des polices de secours."
            )

            # Only show the message box if explicitly requested AND a QApplication exists
            if show_warnings and QApplication.instance() is not None:
                QMessageBox.warning(
                    None,
                    "Erreur de chargement des polices",
                    "La police Inter Variable n'a pas pu être chargée. L'application utilisera des polices de secours.",
                )

        cls._fonts_loaded = True
        return success

    @classmethod
    def get_missing_fonts(cls):
        """Return list of missing font paths if any failed to load."""
        return cls._missing_fonts


@dataclass
class BaseTheme:
    """Base class for widget themes."""

    background_color: str = None
    text_color: str = ThemeConstants.COLORS["dark"]
    border_color: str = ThemeConstants.COLORS["secondary"]
    border_radius: int = ThemeConstants.BORDER_RADIUS["small"]
    font_family: str = ThemeConstants.FONT_FAMILY
    font_size: int = ThemeConstants.FONT_SIZES["default"]
    font_weight: str = "regular"
    font_style: str = "normal"
    padding: Union[int, Tuple[int, int, int, int]] = ThemeConstants.PADDING["default"]

    def __post_init__(self):
        if isinstance(self.padding, int):
            self.padding = (self.padding, self.padding, self.padding, self.padding)

    def get_stylesheet(self) -> str:
        """Generate stylesheet for the widget."""
        raise NotImplementedError

@dataclass
class ButtonTheme(BaseTheme):
    """Theme configuration for QPushButton."""

    border_width: int = 1
    border_radius: int = ThemeConstants.BORDER_RADIUS["medium"]
    hover_background: str = ThemeConstants.COLORS["primary"]
    hover_border_color: str = ThemeConstants.COLORS["primary"]
    pressed_background: str = ThemeConstants.COLORS["primary"]
    pressed_border_color: str = ThemeConstants.COLORS["primary"]
    disabled_opacity: float = 0.65
    font_weight: str = "bold"
    font_style: str = "normal"

    def get_stylesheet(self) -> str:
        """Generate QPushButton stylesheet."""
        return f"""
            QPushButton {{
                background-color: {self.background_color};
                color: {self.text_color};
                border-radius: {self.border_radius}px;
                padding: 0 15px;
                font-family: {self.font_family};
                font-size: {self.font_size}px;
                font-weight: {self.font_weight};
                font-style: {self.font_style};
                border: {self.border_width}px solid {self.border_color};
                outline: none;
            }}

            QPushButton:hover {{
                background-color: {self.hover_background};
                border-color: {self.hover_border_color};
            }}

            QPushButton:pressed {{
                background-color: {self.pressed_background};
                border-color: {self.pressed_border_color};
            }}

            QPushButton:disabled {{
                opacity: {self.disabled_opacity};
            }}
        """

@dataclass
class ComboBoxTheme(BaseTheme):
    """Theme configuration for QComboBox."""
    
    focus_border_color: str = ThemeConstants.COLORS["primary"]
    dropdown_background: str = ThemeConstants.COLORS["white"]
    hover_background: str = ThemeConstants.COLORS["light"]
    selected_background: str = ThemeConstants.COLORS["primary"]
    selected_text_color: str = ThemeConstants.COLORS["white"]
    disabled_background: str = ThemeConstants.COLORS["light"]
    disabled_text_color: str = ThemeConstants.COLORS["muted"]
    error_border_color: str = ThemeConstants.COLORS["danger"]
    item_height: int = 25

    def get_stylesheet(self) -> str:
        """Generate QComboBox stylesheet."""
        return f"""
            QComboBox {{
                background-color: {self.background_color};
                color: {self.text_color};
                border: 1px solid {self.border_color};
                border-radius: {self.border_radius}px;
                padding: 8px 12px;
                font-family: {self.font_family};
                font-size: {self.font_size}px;
                font-weight: {self.font_weight};
            }}
            
            QComboBox:focus {{
                border: 2px solid {self.focus_border_color};
                outline: none;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {self.dropdown_background};
                border: 1px solid {self.border_color};
                border-radius: {self.border_radius}px;
                selection-background-color: {self.selected_background};
                selection-color: {self.selected_text_color};
                outline: none;
                padding: 5px;
            }}

            QComboBox QAbstractItemView::item {{
                background-color: {self.dropdown_background};
                color: {self.text_color};
                padding: 5px;
                min-height: {self.item_height}px;
            }}

            QComboBox QAbstractItemView::item:hover {{
                background-color: {self.hover_background};
            }}

            QComboBox QAbstractItemView::item:selected {{
                background-color: {self.selected_background};
                color: {self.selected_text_color};
            }}

            QComboBox:disabled {{
                background-color: {self.disabled_background};
                color: {self.disabled_text_color};
            }}

            QComboBox[error="true"] {{
                border: 2px solid {self.error_border_color};
            }}

            QComboBox::drop-down {{
                padding-right: 5px;
            }}

            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
        """

@dataclass
class DateFieldTheme(BaseTheme):
    """Theme configuration for QDateEdit."""

    focus_border_color: str = ThemeConstants.COLORS["primary"]
    disabled_background: str = ThemeConstants.COLORS["light"]
    disabled_text_color: str = ThemeConstants.COLORS["muted"]
    calendar_background: str = ThemeConstants.COLORS["dark"]
    calendar_text_color: str = ThemeConstants.COLORS["white"]
    calendar_selected_color: str = ThemeConstants.COLORS["primary"]
    calendar_hover_color: str = ThemeConstants.COLORS["primary"]
    calendar_header_color: str = ThemeConstants.COLORS["dark"]
    calendar_cell_color: str = ThemeConstants.COLORS["dark"]
    calendar_cell_background: str = ThemeConstants.COLORS["white"]
    calendar_cell_selected_background: str = ThemeConstants.COLORS["primary"]
    calendar_cell_hover_background: str = ThemeConstants.COLORS["light"]
    calendar_cell_selected_color: str = ThemeConstants.COLORS["white"]

    def get_stylesheet(self) -> str:
        """Generate QDateEdit stylesheet."""
        return f"""
            QDateEdit {{
                background-color: {self.background_color};
                color: {self.text_color};
                border: 1px solid {self.border_color};
                border-radius: {self.border_radius}px;
                padding: 8px 12px;
                font-family: {self.font_family};
                font-size: {self.font_size}px;
                font-weight: {self.font_weight};
            }}

            QDateEdit:focus {{
                border: 2px solid {self.focus_border_color};
                outline: none;
            }}

            QDateEdit:disabled {{
                background-color: {self.disabled_background};
                color: {self.disabled_text_color};
            }}

            QDateEdit::drop-down {{
                width: 15px;
            }}

            QCalendarWidget QWidget {{
                background-color: {self.calendar_background};
            }}
            
            QCalendarWidget QToolButton {{
                color: {self.calendar_header_color};
                background-color: transparent;
                margin: 2px;
                padding: 5px;
                border-radius: {self.border_radius}px;
            }}

            QCalendarWidget QMenu {{
                background-color: {self.calendar_background};
                color: {self.calendar_header_color};
                border: 1px solid {self.border_color};
            }}

            QCalendarWidget QSpinBox {{
                color: {self.calendar_header_color};
                background-color: {self.calendar_background};
                selection-background-color: {self.calendar_selected_color};
                selection-color: {self.text_color};
            }}

            QCalendarWidget QTableView {{
                background-color: {self.calendar_background};
                outline: 0;
            }}

            QCalendarWidget QAbstractItemView:enabled {{
                color: {self.calendar_cell_color};
                background-color: {self.calendar_cell_background};
                selection-background-color: {self.calendar_cell_selected_background};
                selection-color: {self.calendar_cell_selected_color};
            }}

            QCalendarWidget QAbstractItemView:disabled {{
                color: {self.disabled_text_color};
            }}
            
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background-color: {self.calendar_background};
            }}
            
            QCalendarWidget QAbstractItemView:hover {{
                background-color: {self.calendar_cell_hover_background};
            }}
        """

@dataclass
class TableTheme(BaseTheme):
    """Theme configuration for TableView."""
    
    alternate_background_color: str = ThemeConstants.COLORS["light"]
    selection_background_color: str = ThemeConstants.COLORS["primary"]
    selection_text_color: str = ThemeConstants.COLORS["white"]
    gridline_color: str = ThemeConstants.COLORS["table-border"]
    header_background_color: str = ThemeConstants.COLORS["light-dark"]
    header_text_color: str = ThemeConstants.COLORS["dark"]
    header_border_color: str = ThemeConstants.COLORS["table-border"]
    hover_background_color: str = ThemeConstants.COLORS["table-hover"]  
    border_radius: int = ThemeConstants.BORDER_RADIUS["table"]  
    cell_padding: Tuple[int, int, int, int] = ThemeConstants.PADDING["table-cell"]
    context_menu_background: str = "#ffffff"
    context_menu_text: str = "#1f2937"
    context_menu_hover_background: str = "#f3f4f6"
    context_menu_hover_text: str = "#111827"
    context_menu_border: str = "#e5e7eb"
    context_menu_separator: str = "#e5e7eb"

    def get_stylesheet(self) -> str:
        """Generate QSS stylesheet for QTableView with Bootstrap styling."""
        return f"""
            QTableView {{
                background-color: {self.background_color};
                alternate-background-color: {self.alternate_background_color};
                selection-background-color: {self.selection_background_color};
                selection-color: {self.selection_text_color};
                gridline-color: {self.gridline_color};
                color: {self.text_color};
                font-family: {self.font_family};
                font-size: {self.font_size}px;
                font-weight: {self.font_weight};
                border: 1px solid {self.gridline_color};
                border-radius: {self.border_radius}px;
                outline: 0;
            }}
            QTableView::item {{
                padding: {self.cell_padding[0]}px {self.cell_padding[1]}px {self.cell_padding[2]}px {self.cell_padding[3]}px;
                border: none;
            }}
            QTableView::item:hover {{
                background-color: {self.hover_background_color};
            }}
            QTableView::item:selected {{
                background-color: {self.selection_background_color};
                color: {self.selection_text_color};
            }}
            QTableView::item:focus {{
                outline: none;
            }}
            QHeaderView::section {{
                background-color: {self.header_background_color};
                color: {self.header_text_color};
                padding: 6px 12px;
                border: none;
                border-right: 1px solid {self.header_border_color};
                border-bottom: 1px solid {self.header_border_color};
                font-weight: bold;
                font-family: {self.font_family};
                font-size: {self.font_size}px;
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
            /* Menu Contextuel */
            QMenu {{
                background-color: {self.context_menu_background};
                color: {self.context_menu_text};
                border: 1px solid {self.context_menu_border};
                border-radius: 4px;
                padding: 4px;
            }}

            QMenu::item {{
                padding: 6px 24px;
                border-radius: 2px;
            }}

            QMenu::item:selected {{
                background-color: {self.context_menu_hover_background};
                color: {self.context_menu_hover_text};
            }}

            QMenu::separator {{
                height: 1px;
                background-color: {self.context_menu_separator};
                margin: 4px 0px;
            }}
        """
        
@dataclass
class TextFieldTheme(BaseTheme):
    """Theme configuration for QLineEdit."""

    background_color: str = ThemeConstants.COLORS["white"]
    focus_border_color: str = ThemeConstants.COLORS["primary"]
    error_border_color: str = ThemeConstants.COLORS["danger"]
    disabled_background: str = ThemeConstants.COLORS["light"]
    disabled_text_color: str = ThemeConstants.COLORS["muted"]
    placeholder_color: str = ThemeConstants.COLORS["muted"]
    height: int = ThemeConstants.HEIGHT["default"]

    def get_stylesheet(self) -> str:
        """Generate QLineEdit stylesheet."""
        return f"""
            QLineEdit {{
                background-color: {self.background_color};
                color: {self.text_color};
                border: 1px solid {self.border_color};
                border-radius: {self.border_radius}px;
                padding: 8px 12px;
                font-family: {self.font_family};
                font-size: {self.font_size}px;
                font-weight: {self.font_weight};
            }}

            QLineEdit::placeholder {{
                color: {self.placeholder_color};
            }}

            QLineEdit:focus {{
                border: 2px solid {self.focus_border_color};
                outline: none;
            }}

            QLineEdit[error="true"] {{
                border: 2px solid {self.error_border_color};
            }}

            QLineEdit:disabled {{
                background-color: {self.disabled_background};
                color: {self.disabled_text_color};
            }}

            QLineEdit[valid="false"] {{
                border: 2px solid {self.error_border_color};
            }}

            QLineEdit[valid="false"]:focus {{
                border: 2px solid {self.error_border_color};
            }}
        """

@dataclass
class TextTheme(BaseTheme):
    """Theme configuration for QLabel."""

    align: str = "left"
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    letter_spacing: int = 0
    line_height: float = 1.5
    border_width: int = 0
    hover_color: Optional[str] = None
    hover_background: Optional[str] = None

    def get_stylesheet(self) -> str:
        """Generate QLabel stylesheet."""
        # Font variation settings pour Inter Variable

        style = f"""
            color: {self.text_color};
            font-family: {self.font_family};
            font-size: {self.font_size}px;
            letter-spacing: {self.letter_spacing}px;
            line-height: {self.line_height};
            font-style: {"italic" if self.italic else "normal"};
            text-decoration: {self._get_text_decoration()};
            font-weight: {self.font_weight};
            text-align: {self.align};
            
            qproperty-wordWrap: true;
        """

        if self.background_color:
            style += f"background-color: {self.background_color};"

        if any(self.padding):
            style += f"padding: {self.padding[0]}px {self.padding[1]}px {self.padding[2]}px {self.padding[3]}px;"

        if self.border_radius:
            style += f"border-radius: {self.border_radius}px;"

        if self.border_width and self.border_color:
            style += f"border: {self.border_width}px solid {self.border_color};"

        hover_style = ""
        if self.hover_color:
            hover_style += f"color: {self.hover_color};"
        if self.hover_background:
            hover_style += f"background-color: {self.hover_background};"

        return f"""
            QLabel {{
                {style}
            }}
            
            QLabel:hover {{
                {hover_style if hover_style else f"color: {self.text_color};"}
            }}
        """

    def _get_text_decoration(self) -> str:
        """Handle combined text decorations."""
        decorations = []
        if self.underline:
            decorations.append("underline")
        if self.strikethrough:
            decorations.append("line-through")
        return " ".join(decorations) if decorations else "none"

    def with_modifications(self, **kwargs) -> "TextTheme":
        """Create a new instance with specific modifications."""
        new_attrs = self.__dict__.copy()
        new_attrs.update(kwargs)
        return TextTheme(**new_attrs)

@dataclass
class TextAreaTheme(BaseTheme):
    """Theme configuration for TextArea."""

    background_color: str = ThemeConstants.COLORS["white"]
    focus_border_color: str = ThemeConstants.COLORS["primary"]
    error_border_color: str = ThemeConstants.COLORS["danger"]
    disabled_background: str = ThemeConstants.COLORS["light"]
    disabled_text_color: str = ThemeConstants.COLORS["muted"]
    placeholder_color: str = ThemeConstants.COLORS["muted"]

    def get_stylesheet(self) -> str:
        return f"""
            QTextEdit {{
                background-color: {self.background_color};
                color: {self.text_color};
                border: 1px solid {self.border_color};
                border-radius: {self.border_radius}px;
                padding: 8px;
                font-family: {self.font_family};
                font-size: {self.font_size}px;
            }}

            QTextEdit:focus {{
                border: 2px solid {self.focus_border_color};
                outline: none;
            }}

            QTextEdit:disabled {{
                background-color: {self.disabled_background};
                color: {self.disabled_text_color};
            }}

            QTextEdit[error="true"] {{
                border: 2px solid {self.error_border_color};
            }}
        """

@dataclass
class CheckboxTheme(BaseTheme):
    """Theme configuration for Checkbox."""

    check_color: str = ThemeConstants.COLORS["primary"]
    hover_background: str = ThemeConstants.COLORS["light"]
    disabled_background: str = ThemeConstants.COLORS["light"]
    disabled_text_color: str = ThemeConstants.COLORS["muted"]

    def get_stylesheet(self) -> str:
        return f"""
            QCheckBox {{
                color: {self.text_color};
                font-family: {self.font_family};
                font-size: {self.font_size}px;
                spacing: 5px;
            }}

            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {self.border_color};
                border-radius: 3px;
                background-color: {self.background_color};
            }}

            QCheckBox::indicator:hover {{
                background-color: {self.hover_background};
            }}

            QCheckBox::indicator:checked {{
                background-color: {self.check_color};
                border-color: {self.check_color};
            }}

            QCheckBox::indicator:indeterminate {{
                background-color: {self.check_color};
                border-color: {self.check_color};
            }}

            QCheckBox:disabled {{
                color: {self.disabled_text_color};
            }}

            QCheckBox::indicator:disabled {{
                background-color: {self.disabled_background};
                border-color: {self.disabled_text_color};
            }}
        """

@dataclass
class FileFieldTheme(BaseTheme):
    """Theme configuration for FileField."""

    button_background: str = ThemeConstants.COLORS["primary"]
    button_text_color: str = ThemeConstants.COLORS["white"]
    button_hover_background: str = ThemeConstants.COLORS["primary-dark"]
    info_text_color: str = ThemeConstants.COLORS["secondary"]
    disabled_background: str = ThemeConstants.COLORS["light"]
    disabled_text_color: str = ThemeConstants.COLORS["muted"]

    def get_stylesheet(self) -> str:
        return f"""
            QPushButton {{
                background-color: {self.button_background};
                color: {self.button_text_color};
                border: none;
                border-radius: {self.border_radius}px;
                padding: 8px 16px;
                font-family: {self.font_family};
                font-size: {self.font_size}px;
            }}

            QPushButton:hover {{
                background-color: {self.button_hover_background};
            }}

            QPushButton:disabled {{
                background-color: {self.disabled_background};
                color: {self.disabled_text_color};
            }}

            QLabel {{
                color: {self.info_text_color};
                font-family: {self.font_family};
                font-size: {self.font_size}px;
            }}
        """


@dataclass
class FormTheme(BaseTheme):
    """Theme configuration for Form widgets."""

    background_color: str = ThemeConstants.COLORS["white"]

    submit_button_theme: Optional[ButtonTheme] = None
    cancel_button_theme: Optional[ButtonTheme] = None

    def get_stylesheet(self) -> str:
        """Generate Form stylesheet."""
        return f"""
            /* Style spécifique pour le conteneur du formulaire */
            QWidget {{
                background-color: {self.background_color};
            }}
        """

@dataclass
class MessageBoxTheme(BaseTheme):
    """Configuration du thème pour MessageBox."""
    
    # Couleurs de base
    background_color: str = "#ffffff"
    border_color: str = "#e5e7eb"
    border_radius: int = 8
    
    # Titre
    title_color: str = "#111827"
    title_font_size: str = "16px"
    title_font_weight: str = "bold"
    
    # Message
    message_color: str = "#374151"
    message_font_size: str = "14px"
    
    # Séparateur
    separator_color: str = "#e5e7eb"
    
    # Ombre
    shadow_color: str = "rgba(0, 0, 0, 0.1)"
    shadow_blur: int = 10
    shadow_spread: int = 0
    
    # Dimensions
    min_width: int = 400
    min_height: int = 200
    padding: int = 24
    button_spacing: int = 8
    
    def get_stylesheet(self) -> str:
        return f"""
        QDialog {{
            background: transparent;
        }}
        
        #messageBoxFrame {{
            background-color: {self.background_color};
            border: 1px solid {self.border_color};
            border-radius: {self.border_radius}px;
        }}
        
        #messageBoxSeparator {{
            background-color: {self.separator_color};
            height: 1px;
        }}
        """
        
@dataclass
class SeparatorTheme(BaseTheme):
    """Thème pour le widget Separator"""
    color: str = "#E0E0E0"
    height: int = 1
    margin_top: int = 10
    margin_bottom: int = 10
    
    def get_stylesheet(self) -> str:
        return f"""
            background-color: {self.color};
            max-height: {self.height}px;
            margin-top: {self.margin_top}px;
            margin-bottom: {self.margin_bottom}px;
        """

@dataclass
class ProgressBarTheme(BaseTheme):
    """Theme configuration for QProgressBar."""
    background_color: str = "#D6E2E2"
    chunk_color: str = ThemeConstants.COLORS["primary"]
    text_color: str = ThemeConstants.COLORS["dark"]
    border_color: str = ThemeConstants.COLORS["primary"]
    border_radius: int = 5
    height: int = 24

    def get_stylesheet(self) -> str:
        return f"""
            QWidget#progress-bar {{
                background-color: {self.background_color};
            }}
            QProgressBar {{
                background-color: {self.background_color};
                color: {self.text_color};
                border: 1px solid {self.border_color};
                border-radius: {self.border_radius}px;
                text-align: center;
                height: {self.height}px;
                font-family: {self.font_family};
                font-size: {self.font_size}px;
            }}
            QProgressBar::chunk {{
                background-color: {self.chunk_color};
                border-radius: {self.border_radius}px;
            }}
        """
class ThemeManager:
    """Centralized manager for widget themes."""

    _initialized = False

    @classmethod
    def ensure_fonts_loaded(cls, show_warnings=False):
        """Ensure fonts are loaded if possible."""
        return FontLoader.load_fonts(show_warnings=show_warnings)

    @staticmethod
    def show_missing_fonts_warning():
        """Show warning dialog about missing fonts if any and if QApplication exists."""
        missing_fonts = FontLoader._missing_fonts
        if missing_fonts and QApplication.instance() is not None:
            missing_list = "\n".join(missing_fonts)
            QMessageBox.warning(
                None,
                "Polices manquantes",
                f"Les polices suivantes n'ont pas pu être chargées:\n{missing_list}\n\n"
                f"L'application utilisera des polices de secours.",
            )

    @classmethod
    def initialize(cls, show_warnings=False):
        """Initialize the theme manager by loading fonts.

        Args:
            show_warnings: Whether to show warning dialogs for font loading issues.
            Only set to True after QApplication is initialized.
        """
        if not cls._initialized:
            # Load fonts but don't show UI warnings unless explicitly requested
            FontLoader.load_fonts(show_warnings=show_warnings)
            cls._initialized = True
            logger.info("ThemeManager initialized")

    class ButtonThemes:
        """Predefined button themes."""

        PRIMARY = ButtonTheme(
            background_color=ThemeConstants.COLORS["primary"],
            text_color=ThemeConstants.COLORS["white"],
            border_color=ThemeConstants.COLORS["primary"],
            hover_background="#0056b3",
            hover_border_color="#0056b3",
            pressed_background="#004085",
            pressed_border_color="#004085",
            font_weight="bold",
        )

        SECONDARY = ButtonTheme(
            background_color=ThemeConstants.COLORS["secondary"],
            text_color=ThemeConstants.COLORS["white"],
            border_color=ThemeConstants.COLORS["secondary"],
            hover_background="#5a6268",
            hover_border_color="#5a6268",
            pressed_background="#4e555b",
            pressed_border_color="#4e555b",
            font_weight="bold",
        )

        SUCCESS = ButtonTheme(
            background_color=ThemeConstants.COLORS["success"],
            text_color=ThemeConstants.COLORS["white"],
            border_color=ThemeConstants.COLORS["success"],
            hover_background="#157347",
            hover_border_color="#157347",
            pressed_background="#126d3e",
            pressed_border_color="#126d3e",
            font_weight="bold",
        )

        DANGER = ButtonTheme(
            background_color=ThemeConstants.COLORS["danger"],
            text_color=ThemeConstants.COLORS["white"],
            border_color=ThemeConstants.COLORS["danger"],
            hover_background="#bb2d3b",
            hover_border_color="#bb2d3b",
            pressed_background="#a12835",
            pressed_border_color="#a12835",
            font_weight="bold",
        )

        DARK = ButtonTheme(
            background_color=ThemeConstants.COLORS["dark"],
            text_color=ThemeConstants.COLORS["white"],
            border_color=ThemeConstants.COLORS["secondary"],
            hover_background="#5a6268",
            hover_border_color="#5a6268",
            pressed_background="#4e555b",
            pressed_border_color="#4e555b",
            font_weight="bold",
        )

        SIDEBAR_ITEM = ButtonTheme(
            background_color="transparent",
            text_color="#ffffff",  # Couleur de texte gris clair
            border_color="transparent",
            hover_background="#21262d",  # Couleur de survol subtile
            hover_border_color="transparent",
            pressed_background="#2b3139",  # Couleur quand pressé
            pressed_border_color="transparent",
            font_size=16,
            font_weight="bold",
            border_radius=6,
            disabled_opacity=0.65,
        )

        SIDEBAR_ITEM_ACTIVE = ButtonTheme(
            background_color="#2b3139",  # Couleur de fond quand actif
            text_color="#ffffff",  # Texte blanc quand actif
            border_color="transparent",
            hover_background="#2b3139",
            hover_border_color="transparent",
            pressed_background="#2b3139",
            pressed_border_color="transparent",
            font_size=14,
            font_weight="medium",
            border_radius=6,
            disabled_opacity=0.65,
        )

    class ComboBoxThemes:
        """Predefined combobox themes."""

        DEFAULT = ComboBoxTheme(
            background_color=ThemeConstants.COLORS["white"],
        )

        LIGHT = ComboBoxTheme(
            background_color=ThemeConstants.COLORS["white"],
        )

        DARK = ComboBoxTheme(
            background_color=ThemeConstants.COLORS["dark"],
            text_color=ThemeConstants.COLORS["white"],
            border_color=ThemeConstants.COLORS["secondary"],
            dropdown_background=ThemeConstants.COLORS["dark"],
            hover_background="#495057",
            selected_background="#0056b3",
            disabled_background="#495057",
            disabled_text_color="#adb5bd",
        )
        
    class DateFieldThemes:
        """Predefined date field themes."""

        DEFAULT = DateFieldTheme(
            background_color=ThemeConstants.COLORS["white"],
            text_color=ThemeConstants.COLORS["dark"],
            calendar_background=ThemeConstants.COLORS["white"],
        )

        LIGHT = DateFieldTheme(
            background_color=ThemeConstants.COLORS["white"],
            text_color=ThemeConstants.COLORS["dark"],
            calendar_background=ThemeConstants.COLORS["white"],
        )

        DARK = DateFieldTheme(
            background_color=ThemeConstants.COLORS["dark"],
            text_color=ThemeConstants.COLORS["white"],
            border_color=ThemeConstants.COLORS["secondary"],
            calendar_background=ThemeConstants.COLORS["dark"],
            calendar_header_color=ThemeConstants.COLORS["white"],
            calendar_cell_color=ThemeConstants.COLORS["white"],
            calendar_cell_background=ThemeConstants.COLORS["dark"],
            disabled_background="#495057",
            disabled_text_color="#adb5bd",
        )

    class TextFieldThemes:
        """Predefined text field themes."""

        DEFAULT = TextFieldTheme()

        DARK = TextFieldTheme(
            background_color=ThemeConstants.COLORS["dark"],
            text_color=ThemeConstants.COLORS["white"],
            border_color=ThemeConstants.COLORS["secondary"],
            focus_border_color="#0056b3",
            placeholder_color="#adb5bd",
            disabled_background="#495057",
            disabled_text_color="#adb5bd",
        )

    class TextThemes:
        """Predefined text themes."""

        DEFAULT = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
        )

        LOGO = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["logo"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["white"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        H1 = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h1"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        H2 = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h2"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        H3 = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h3"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        H4 = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h4"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        H5 = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h5"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        H6 = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h6"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        # Headings with color variants
        H1_PRIMARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h1"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["primary"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H2_PRIMARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h2"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["primary"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H3_PRIMARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h3"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["primary"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H4_PRIMARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h4"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["primary"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H5_PRIMARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h5"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["primary"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H6_PRIMARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h6"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["primary"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        H1_SECONDARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h1"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["secondary"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H2_SECONDARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h2"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["secondary"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H3_SECONDARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h3"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["secondary"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H4_SECONDARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h4"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["secondary"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H5_SECONDARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h5"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["secondary"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H6_SECONDARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h6"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["secondary"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        H1_SUCCESS = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h1"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["success"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H2_SUCCESS = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h2"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["success"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H3_SUCCESS = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h3"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["success"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H4_SUCCESS = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h4"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["success"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H5_SUCCESS = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h5"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["success"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H6_SUCCESS = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h6"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["success"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        H1_DANGER = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h1"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["danger"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H2_DANGER = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h2"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["danger"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H3_DANGER = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h3"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["danger"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H4_DANGER = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h4"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["danger"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H5_DANGER = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h5"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["danger"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H6_DANGER = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h6"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["danger"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        H1_WARNING = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h1"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["warning"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H2_WARNING = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h2"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["warning"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H3_WARNING = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h3"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["warning"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H4_WARNING = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h4"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["warning"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H5_WARNING = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h5"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["warning"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H6_WARNING = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h6"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["warning"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        H1_INFO = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h1"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["info"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H2_INFO = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h2"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["info"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H3_INFO = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h3"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["info"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H4_INFO = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h4"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["info"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H5_INFO = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h5"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["info"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H6_INFO = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h6"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["info"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        H1_LIGHT = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h1"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["light"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H2_LIGHT = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h2"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["light"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H3_LIGHT = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h3"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["light"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H4_LIGHT = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h4"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["light"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H5_LIGHT = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h5"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["light"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H6_LIGHT = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h6"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["light"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        H1_DARK = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h1"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H2_DARK = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h2"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H3_DARK = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h3"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H4_DARK = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h4"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H5_DARK = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h5"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        H6_DARK = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["h6"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        LEAD = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["lead"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
        )

        BODY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
        )

        BODY_PRIMARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["primary"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
        )

        BODY_SECONDARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["secondary"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
        )

        BODY_SUCCESS = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["success"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
        )

        BODY_DANGER = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["danger"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
        )

        BODY_WARNING = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["warning"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
        )

        BODY_INFO = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["info"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
        )

        BODY_LIGHT = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["light"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
        )

        BODY_DARK = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
        )

        PRIMARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["primary"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
            hover_color="#0a58ca",
            border_radius=ThemeConstants.BORDER_RADIUS["small"],
        )

        SECONDARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["secondary"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
        )

        SUCCESS = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["success"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
        )

        DANGER = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["danger"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
        )

        WARNING = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["warning"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
        )

        INFO = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["info"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
        )

        LIGHT = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["light"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
        )

        DARK = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
        )

        BUTTON_PRIMARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="medium",
            text_color=ThemeConstants.COLORS["white"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
            background_color=ThemeConstants.COLORS["primary"],
            border_radius=ThemeConstants.BORDER_RADIUS["medium"],
            padding=ThemeConstants.PADDING["medium"],
            hover_background="#0b5ed7",
        )

        BUTTON_SECONDARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="medium",
            text_color=ThemeConstants.COLORS["white"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
            background_color=ThemeConstants.COLORS["secondary"],
            border_radius=ThemeConstants.BORDER_RADIUS["medium"],
            padding=ThemeConstants.PADDING["medium"],
            hover_background="#5c636a",
        )

        BUTTON_SUCCESS = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="medium",
            text_color=ThemeConstants.COLORS["white"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
            background_color=ThemeConstants.COLORS["success"],
            border_radius=ThemeConstants.BORDER_RADIUS["medium"],
            padding=ThemeConstants.PADDING["medium"],
            hover_background="#157347",
        )

        BUTTON_DANGER = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="medium",
            text_color=ThemeConstants.COLORS["white"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
            background_color=ThemeConstants.COLORS["danger"],
            border_radius=ThemeConstants.BORDER_RADIUS["medium"],
            padding=ThemeConstants.PADDING["medium"],
            hover_background="#bb2d3b",
        )

        BUTTON_WARNING = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="medium",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
            background_color=ThemeConstants.COLORS["warning"],
            border_radius=ThemeConstants.BORDER_RADIUS["medium"],
            padding=ThemeConstants.PADDING["medium"],
            hover_background="#e0a800",
        )

        BUTTON_INFO = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="medium",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
            background_color=ThemeConstants.COLORS["info"],
            border_radius=ThemeConstants.BORDER_RADIUS["medium"],
            padding=ThemeConstants.PADDING["medium"],
            hover_background="#0aa2c0",
        )

        BUTTON_LIGHT = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="medium",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
            background_color=ThemeConstants.COLORS["light"],
            border_radius=ThemeConstants.BORDER_RADIUS["medium"],
            padding=ThemeConstants.PADDING["medium"],
            hover_background="#e2e6ea",
        )

        BUTTON_DARK = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="medium",
            text_color=ThemeConstants.COLORS["white"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.5,
            background_color=ThemeConstants.COLORS["dark"],
            border_radius=ThemeConstants.BORDER_RADIUS["medium"],
            padding=ThemeConstants.PADDING["medium"],
            hover_background="#343a40",
        )

        BADGE_LIGHT = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["badge"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            align="center",
            background_color=ThemeConstants.COLORS["light"],
            border_radius=ThemeConstants.BORDER_RADIUS["large"],
            padding=ThemeConstants.PADDING["badge"],
        )

        BADGE_DARK = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["badge"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["white"],
            font_family=ThemeConstants.FONT_FAMILY,
            align="center",
            background_color=ThemeConstants.COLORS["dark"],
            border_radius=ThemeConstants.BORDER_RADIUS["large"],
            padding=ThemeConstants.PADDING["badge"],
        )
        BADGE_PRIMARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["badge"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["white"],
            font_family=ThemeConstants.FONT_FAMILY,
            align="center",
            background_color=ThemeConstants.COLORS["primary"],
            border_radius=ThemeConstants.BORDER_RADIUS["large"],
            padding=ThemeConstants.PADDING["badge"],
        )
        BADGE_SECONDARY = TextTheme(
            font_size=ThemeConstants.FONT_FAMILY,
            font_weight="bold",
            text_color=ThemeConstants.COLORS["white"],
            font_family=ThemeConstants.FONT_FAMILY,
            align="center",
            background_color=ThemeConstants.COLORS["secondary"],
            border_radius=ThemeConstants.BORDER_RADIUS["large"],
            padding=ThemeConstants.PADDING["badge"],
        )

        BADGE_SUCCESS = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["badge"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["white"],
            font_family=ThemeConstants.FONT_FAMILY,
            align="center",
            background_color=ThemeConstants.COLORS["success"],
            border_radius=ThemeConstants.BORDER_RADIUS["large"],
            padding=ThemeConstants.PADDING["badge"],
        )

        BADGE_DANGER = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["badge"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["white"],
            font_family=ThemeConstants.FONT_FAMILY,
            align="center",
            background_color=ThemeConstants.COLORS["danger"],
            border_radius=ThemeConstants.BORDER_RADIUS["large"],
            padding=ThemeConstants.PADDING["badge"],
        )
        BADGE_WARNING = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["badge"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            align="center",
            background_color=ThemeConstants.COLORS["warning"],
            border_radius=ThemeConstants.BORDER_RADIUS["large"],
            padding=ThemeConstants.PADDING["badge"],
        )
        BADGE_INFO = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["badge"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            align="center",
            background_color=ThemeConstants.COLORS["info"],
            border_radius=ThemeConstants.BORDER_RADIUS["large"],
            padding=ThemeConstants.PADDING["badge"],
        )

        LABEL_NB = TextTheme(
            font_size=14,
            font_weight="bold",
            text_color=ThemeConstants.COLORS["danger"],
            font_family=ThemeConstants.FONT_FAMILY,
        )

        ITALIC = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            italic=True,
        )

        BOLD = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="bold",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
        )

        LINK_PRIMARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["primary"],
            font_family=ThemeConstants.FONT_FAMILY,
            underline=True,
            hover_color="#0a58ca",
            align="left",
        )

        LINK_SECONDARY = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["secondary"],
            font_family=ThemeConstants.FONT_FAMILY,
            underline=True,
            hover_color="#5c636a",
            align="left",
        )

        LINK_SUCCESS = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["success"],
            font_family=ThemeConstants.FONT_FAMILY,
            underline=True,
            hover_color="#157347",
            align="left",
        )

        LINK_DANGER = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["danger"],
            font_family=ThemeConstants.FONT_FAMILY,
            underline=True,
            hover_color="#bb2d3b",
            align="left",
        )

        LINK_WARNING = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["warning"],
            font_family=ThemeConstants.FONT_FAMILY,
            underline=True,
            hover_color="#e0a800",
            align="left",
        )

        LINK_INFO = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["default"],
            font_weight="regular",
            text_color=ThemeConstants.COLORS["info"],
            font_family=ThemeConstants.FONT_FAMILY,
            underline=True,
            hover_color="#0aa2c0",
            align="left",
        )

        ERROR = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["small"],
            text_color=ThemeConstants.COLORS["danger"],
            font_family=ThemeConstants.FONT_FAMILY,
            italic=True,
        )

        HELPER = TextTheme(
            font_size=ThemeConstants.FONT_SIZES["small"],
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            italic=True,
        )

        DISPLAY1 = TextTheme(
            font_size=72,
            font_weight="light",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        DISPLAY2 = TextTheme(
            font_size=64,
            font_weight="light",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        DISPLAY3 = TextTheme(
            font_size=56,
            font_weight="light",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        DISPLAY4 = TextTheme(
            font_size=48,
            font_weight="light",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        # Label themes
        LABEL = TextTheme(
            font_size=14,
            font_weight="bold",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            align="left",
            line_height=1.2,
        )

        LABEL_CENTER = TextTheme(
            font_size=14,
            font_weight="regular",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            align="center",
            line_height=1.2,
        )

        LABEL_RIGHT = TextTheme(
            font_size=14,
            font_weight="regular",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            align="right",
            line_height=1.2,
        )

        # Label color variants
        LABEL_PRIMARY = TextTheme(
            font_size=14,
            font_weight="regular",
            text_color=ThemeConstants.COLORS["primary"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        LABEL_SECONDARY = TextTheme(
            font_size=14,
            font_weight="regular",
            text_color=ThemeConstants.COLORS["secondary"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        LABEL_SUCCESS = TextTheme(
            font_size=14,
            font_weight="regular",
            text_color=ThemeConstants.COLORS["success"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        LABEL_DANGER = TextTheme(
            font_size=14,
            font_weight="regular",
            text_color=ThemeConstants.COLORS["danger"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        LABEL_WARNING = TextTheme(
            font_size=14,
            font_weight="regular",
            text_color=ThemeConstants.COLORS["warning"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        LABEL_INFO = TextTheme(
            font_size=14,
            font_weight="regular",
            text_color=ThemeConstants.COLORS["info"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        LABEL_LIGHT = TextTheme(
            font_size=14,
            font_weight="regular",
            text_color=ThemeConstants.COLORS["light"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )

        LABEL_DARK = TextTheme(
            font_size=14,
            font_weight="regular",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        
        CARD_TITLE_LABEL = TextTheme(
            font_size=14,
            font_weight="bold",
            text_color=ThemeConstants.COLORS["card-title"],
            font_family=ThemeConstants.FONT_FAMILY,
            align="right",
            line_height=1.2,
        )

        CARD_VALUE_LABEL = TextTheme(
            font_size=40,
            font_weight="bold",
            text_color=ThemeConstants.COLORS["card-value"],
            font_family=ThemeConstants.FONT_FAMILY,
            align="right",
            line_height=1.2,
        )
        
        CARD_ICON_LABEL = TextTheme(
            font_size=14,
            font_weight="bold",
            text_color=ThemeConstants.COLORS["dark"],
            font_family=ThemeConstants.FONT_FAMILY,
            align="center",
            line_height=1.2,
        )
        
        CARD_FOOTER_LABEL = TextTheme(
            font_size=12,
            font_weight="bold",
            text_color=ThemeConstants.COLORS["card-footer"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        
        DASHBOARD_FOOTER_LABEL = TextTheme(
            font_size=12,
            font_weight="bold",
            text_color=ThemeConstants.COLORS["card-footer"],
            font_family=ThemeConstants.FONT_FAMILY,
            line_height=1.2,
        )
        
    class TextAreaThemes:
        """Predefined textarea themes."""

        DEFAULT = TextAreaTheme()

        LIGHT = TextAreaTheme(
            background_color=ThemeConstants.COLORS["light"],
            text_color=ThemeConstants.COLORS["dark"],
        )

        DARK = TextAreaTheme(
            background_color=ThemeConstants.COLORS["dark"],
            text_color=ThemeConstants.COLORS["white"],
            border_color=ThemeConstants.COLORS["secondary"],
        )

    class CheckboxThemes:
        """Predefined checkbox themes."""

        DEFAULT = CheckboxTheme()

        LIGHT = CheckboxTheme(
            background_color=ThemeConstants.COLORS["light"],
            text_color=ThemeConstants.COLORS["dark"],
        )

        DARK = CheckboxTheme(
            background_color=ThemeConstants.COLORS["dark"],
            text_color=ThemeConstants.COLORS["white"],
            border_color=ThemeConstants.COLORS["secondary"],
            check_color=ThemeConstants.COLORS["info"],
        )

    class FileFieldThemes:
        """Predefined file field themes."""

        DEFAULT = FileFieldTheme()

        LIGHT = FileFieldTheme(
            button_background=ThemeConstants.COLORS["light"],
            button_text_color=ThemeConstants.COLORS["dark"],
            button_hover_background=ThemeConstants.COLORS["light-dark"],
        )

        DARK = FileFieldTheme(
            button_background=ThemeConstants.COLORS["dark"],
            button_text_color=ThemeConstants.COLORS["white"],
            info_text_color=ThemeConstants.COLORS["light"],
            button_hover_background=ThemeConstants.COLORS["dark-light"],
        )

    class FormThemes:
        """Predefined form themes."""

        DEFAULT = FormTheme(
            background_color=ThemeConstants.COLORS["white"],
            submit_button_theme=ButtonTheme(
                background_color=ThemeConstants.COLORS["primary"],
                text_color=ThemeConstants.COLORS["white"],
                border_color=ThemeConstants.COLORS["primary"],
                hover_background="#0056b3",
                hover_border_color="#0056b3",
                pressed_background="#004085",
                pressed_border_color="#004085",
                font_weight="bold",
            ),
            cancel_button_theme=ButtonTheme(
                background_color=ThemeConstants.COLORS["danger"],
                text_color=ThemeConstants.COLORS["white"],
                border_color=ThemeConstants.COLORS["danger"],
                hover_background="#bb2d3b",
                hover_border_color="#bb2d3b",
                pressed_background="#a12835",
                pressed_border_color="#a12835",
                font_weight="bold",
            )
        )

    class SeparatorThemes:
        DEFAULT = SeparatorTheme(
            color="#E0E0E0",
            height=1,
            margin_top=10,
            margin_bottom=10
        )
        
    class TableThemes:
        """Predefined table themes."""
        
        LIGHT = TableTheme(
            background_color=ThemeConstants.COLORS["white"],
            alternate_background_color="#f8f9fa",  # Bootstrap table-striped
            text_color=ThemeConstants.COLORS["dark"],
            selection_background_color=ThemeConstants.COLORS["primary"],
            selection_text_color=ThemeConstants.COLORS["white"],
            gridline_color=ThemeConstants.COLORS["table-border"],
            header_background_color="#e9ecef",  # Bootstrap table header
            header_text_color=ThemeConstants.COLORS["dark"],
            header_border_color=ThemeConstants.COLORS["table-border"],
            hover_background_color=ThemeConstants.COLORS["table-hover"],
            border_radius=ThemeConstants.BORDER_RADIUS["table"],
            cell_padding=ThemeConstants.PADDING["table-cell"],
            font_family=ThemeConstants.FONT_FAMILY,
            font_size=ThemeConstants.FONT_SIZES["default"],
            context_menu_background="#ffffff",
            context_menu_text="#1f2937",
            context_menu_hover_background="#f3f4f6",
            context_menu_hover_text="#111827",
            context_menu_border="#e5e7eb",
            context_menu_separator="#e5e7eb"
        )

        DARK = TableTheme(
            background_color="#212529",  # Bootstrap table-dark
            alternate_background_color="#2c3236",
            text_color="#d4d4d4",
            selection_background_color=ThemeConstants.COLORS["primary"],
            selection_text_color=ThemeConstants.COLORS["white"],
            gridline_color="#495057",
            header_background_color="#343a40",
            header_text_color="#d4d4d4",
            header_border_color="#495057",
            hover_background_color="#3a4147",
            border_radius=ThemeConstants.BORDER_RADIUS["table"],
            cell_padding=ThemeConstants.PADDING["table-cell"],
            font_family=ThemeConstants.FONT_FAMILY,
            font_size=ThemeConstants.FONT_SIZES["default"],
            context_menu_background="#1e1e1e",
            context_menu_text="#d4d4d4",
            context_menu_hover_background="#2a2a2a",
            context_menu_hover_text="#ffffff",
            context_menu_border="#333333",
            context_menu_separator="#333333"
        )

        BLUE = TableTheme(
            background_color=ThemeConstants.COLORS["white"],
            alternate_background_color="#edf5ff",  # Bleu pâle
            text_color=ThemeConstants.COLORS["dark"],
            selection_background_color="#3498db",  # Bleu vif
            selection_text_color=ThemeConstants.COLORS["white"],
            gridline_color="#a3cffa",
            header_background_color="#d1e7ff",  # En-tête bleu clair
            header_text_color=ThemeConstants.COLORS["dark"],
            header_border_color="#a3cffa",
            hover_background_color="#e1f0ff",
            border_radius=ThemeConstants.BORDER_RADIUS["table"],
            cell_padding=ThemeConstants.PADDING["table-cell"],
            font_family=ThemeConstants.FONT_FAMILY,
            font_size=ThemeConstants.FONT_SIZES["default"],
            context_menu_background="#ffffff",
            context_menu_text="#2c3e50",
            context_menu_hover_background="#e1f0ff",
            context_menu_hover_text="#2c3e50",
            context_menu_border="#bde0ff",
            context_menu_separator="#bde0ff"
        )

    class MessageBoxThemes:
        """Thèmes prédéfinis pour MessageBox."""
        
        DEFAULT = MessageBoxTheme()
        
        SUCCESS = MessageBoxTheme(
            border_color="#34D399",
            title_color="#065F46",
            message_color="#065F46",
            separator_color="#6EE7B7"
        )
        
        WARNING = MessageBoxTheme(
            border_color="#FBBF24",
            title_color="#92400E",
            message_color="#92400E",
            separator_color="#FCD34D"
        )
        
        ERROR = MessageBoxTheme(
            border_color="#EF4444",
            title_color="#991B1B",
            message_color="#991B1B",
            separator_color="#FCA5A5"
        )
        
        QUESTION = MessageBoxTheme(
            border_color="#818CF8",
            title_color="#3730A3",
            message_color="#3730A3",
            separator_color="#A5B4FC"
        )
        
    class ProgressBarThemes:
        """Predefined progress bar themes."""
        DEFAULT = ProgressBarTheme()
        PRIMARY = ProgressBarTheme(
            chunk_color=ThemeConstants.COLORS["primary"],
            border_color=ThemeConstants.COLORS["primary"],
        )
        SUCCESS = ProgressBarTheme(
            chunk_color=ThemeConstants.COLORS["success"],
            border_color=ThemeConstants.COLORS["success"],
        )
        DANGER = ProgressBarTheme(
            chunk_color=ThemeConstants.COLORS["danger"],
            border_color=ThemeConstants.COLORS["danger"],
        )
        INFO = ProgressBarTheme(
            chunk_color=ThemeConstants.COLORS["info"],
            border_color=ThemeConstants.COLORS["info"],
        )
        WARNING = ProgressBarTheme(
            chunk_color=ThemeConstants.COLORS["warning"],
            border_color=ThemeConstants.COLORS["warning"],
        )
        SECONDARY = ProgressBarTheme(
            chunk_color=ThemeConstants.COLORS["secondary"],
            border_color=ThemeConstants.COLORS["secondary"],
        )
FontLoader._try_load_fonts()

_original_qapp_init = QApplication.__init__


def _patched_qapp_init(self, *args, **kwargs):
    _original_qapp_init(self, *args, **kwargs)
    FontLoader.load_fonts(show_warnings=False)


QApplication.__init__ = _patched_qapp_init
