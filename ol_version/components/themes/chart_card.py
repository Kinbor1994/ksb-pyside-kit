"""Theme module for card widgets.

This module provides theming capabilities for various card widgets.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class ChartTheme:
    """Theme configuration for chart cards"""
    # Général
    background_color: str = "#FFFFFF"
    border_radius: int = 4
    border_color: str = "rgba(63,63,68,0.1)"
    padding: int = 15
    spacing: int = 5

    # Titre
    title_color: str = "#9A9A9A"
    title_font_size: int = 14
    
    # Séparateur
    separator_color: str = "#EEEEEE"
    separator_height: int = 1
    
    # Description (Footer)
    footer_color: str = "#9A9A9A"
    footer_font_size: int = 12
    
    def get_card_stylesheet(self) -> str:
        """Generate chart card stylesheet"""
        return f"""
            #baseCard {{
                background-color: {self.background_color};
                border-radius: {self.border_radius}px;
                border: 1px solid {self.border_color};
            }}
        """

class ChartThemes:
    """Predefined chart themes"""
    
    LIGHT = ChartTheme()
    
    DARK = ChartTheme(
        background_color="#2C2C2C",
        separator_color="#3F3F3F",
        title_color="#FFFFFF",
        footer_color="#9A9A9A",
    )
    
    BLUE = ChartTheme(
        background_color="#F4F9FE",
        separator_color="#E1E8ED",
        title_color="#1DC7EA",
        footer_color="#7A92A3",
    )