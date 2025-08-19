"""Card widgets module.

This module provides various card widgets for the dashboard using qtawesome icons.
"""
from datetime import  datetime
from typing import Optional

from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Property

from ...core.commons import QFrame, QVBoxLayout, QHBoxLayout, QWidget, Qt, QTimer
from ...widgets.text import Text
from ..themes.cards import CardTheme, CardThemes
from ...core.themes.themes import ThemeManager

class BaseCard(QFrame):
    """Base card widget with common styling and structure"""
    
    def __init__(
        self,
        title: str,
        icon: str,
        icon_color: str = "#1DC7EA",
        theme: Optional[CardTheme] = None,
        parent=None
    ):
        super().__init__(parent)
        self.setObjectName("baseCard")
        self.setFixedHeight(150)
        self.setFixedWidth(335)
        
        # Properties
        self.title = title
        self.icon = icon
        self.icon_color = icon_color
        self.theme = theme or CardThemes.LIGHT
        
        # Animation properties
        self._elevation = 0
        
        # Setup UI
        self.setup_ui()
        self.apply_theme()
        
    def setup_ui(self):
        """Initialize the card UI components"""
        # Main layout
        self.layout = QHBoxLayout(self)  # Changed to QHBoxLayout
        self.layout.setContentsMargins(
            self.theme.padding,
            self.theme.padding,
            self.theme.padding,
            self.theme.padding
        )
        self.layout.setSpacing(self.theme.spacing)
        
        # Icon container (left side)
        icon_container = QFrame()
        icon_container.setObjectName("iconContainer")
        icon_container.setFixedSize(self.theme.icon_size + 20, self.theme.icon_size + 20)
        icon_container.setStyleSheet(f"""
            #iconContainer {{
                border-radius: {(self.theme.icon_size + 20) // 2}px;
            }}
        """)
        
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        self.icon_label = Text(
            icon=self.icon,
            icon_size=self.theme.icon_size,
            icon_color=self.icon_color
        )
        icon_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        
        self.layout.addWidget(icon_container)
        
        # Content container (right side)
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(10, 0, 0, 0)
        content_layout.setSpacing(5)
        
        # Title
        self.title_label = Text(
            value=self.title,
            theme=ThemeManager.TextThemes.CARD_TITLE_LABEL
        )
        content_layout.addWidget(self.title_label)
        
        # Store content layout for derived classes
        self.content_layout = content_layout
        self.layout.addWidget(content_container, 1)  # Stretch factor 1
        
    def apply_theme(self):
        """Apply current theme to the card"""
        self.setStyleSheet(self.theme.get_card_stylesheet())

    def enterEvent(self, event):
        """Handle mouse enter event"""
        self._animate_elevation(6)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave event"""
        self._animate_elevation(0)
        super().leaveEvent(event)
    
    def _animate_elevation(self, end_value: int):
        """Animate card elevation"""
        animation = QPropertyAnimation(self, b"elevation", self)
        animation.setDuration(200)
        animation.setStartValue(self._elevation)
        animation.setEndValue(end_value)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()
    
    def _get_elevation(self) -> int:
        return self._elevation
    
    def _set_elevation(self, value: int):
        if self._elevation != value:
            self._elevation = value
            # Mettre à jour les marges pour simuler l'élévation
            self.setContentsMargins(3, 3-value, 3, 3+value)
    
    # Définir la propriété elevation pour l'animation
    elevation = Property(int, _get_elevation, _set_elevation)
    
class StatCard(BaseCard):
    """Statistical card with big number and footer"""
    
    def __init__(
        self,
        title: str,
        value: str,
        description_text: str,
        icon: str,
        icon_color: str = "#1DC7EA",
        theme: Optional[CardTheme] = None,
        parent=None
    ):
        super().__init__(title, icon, icon_color, theme, parent)
        self.value = value
        self.description_text = description_text
        self.theme = theme or CardThemes.LIGHT
        self.setup_content()
        
        # self.last_update_time = datetime.now()
        # self._setup_update_timer()
        
    def setup_content(self):
        """Setup the card content"""
        # Value
        self.value_label = Text(
            value=self.value,
            theme=ThemeManager.TextThemes.CARD_VALUE_LABEL,
        )
        self.content_layout.addWidget(self.value_label)
        
        # Add stretch to push separator to bottom
        self.content_layout.addStretch()
        
        # Separator
        self.separator = QFrame()
        self.separator.setObjectName("separator")
        self.separator.setFixedHeight(self.theme.separator_height)
        self.separator.setStyleSheet(f"""
            #separator {{
                background-color: {self.theme.separator_color};
                margin: 5px 0px;
            }}
        """)
        self.content_layout.addWidget(self.separator)
        
        # Footer
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 5, 0, 0)
        footer_layout.setSpacing(self.theme.footer_spacing)
        
        self.footer_label = Text(
            value=self.description_text,
            width=335,
            theme=ThemeManager.TextThemes.CARD_FOOTER_LABEL,
        )
        
        footer_layout.addWidget(self.footer_label)
        footer_layout.addStretch()
        
        self.content_layout.addLayout(footer_layout)
        
    def update_footer(self, new_text: str):
        """Update the footer text
        
        Args:
            new_text: New footer text
        """
        self.description_text = new_text
        self.footer_label.text = new_text
    
    def update_title(self, new_title: str):
        """Update the card's title
        
        Args:
            new_title: New title text
        """
        self.title = new_title
        self.title_label.text = new_title
        
    def update_value(self, new_value: str):
        """Update the card's main value
        
        Args:
            new_value: New value to display
        """
        self.value = new_value
        self.value_label.text = new_value
        