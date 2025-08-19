"""Theme module for card widgets.

This module provides theming capabilities for various card widgets.
"""

from dataclasses import dataclass

@dataclass
class CardTheme:
    """Theme configuration for card widgets"""
    background_color: str = "#FFFFFF"
    border_radius: int = 4
    border_color: str = "rgba(63,63,68,0.1)"
    padding: int = 15
    spacing: int = 5
    
    # Header
    header_spacing: int = 10
    title_color: str = "#9A9A9A"
    title_font_size: int = 14
    icon_size: int = 24
    
    # Separator
    separator_color: str = "#EEEEEE"
    separator_height: int = 1
    
    # Content
    value_color: str = "#252422"
    value_font_size: int = 25
    value_font_weight: str = "bold"
    
    # Footer
    footer_color: str = "#9A9A9A"
    footer_font_size: int = 12
    footer_spacing: int = 5

    def get_card_stylesheet(self) -> str:
        """Generate card stylesheet"""
        return f"""
            #baseCard {{
                background-color: {self.background_color};
                border-radius: {self.border_radius}px;
                border: 1px solid {self.border_color};
                margin: 3px 3px 3px 3px;
            }}
            
            #baseCard:hover {{
                margin: 0px 3px 6px 3px;
            }}
        """

class CardThemes:
    """Predefined card themes"""
    
    LIGHT = CardTheme()
    
    DARK = CardTheme(
        background_color="#2C2C2C",
        separator_color="#3F3F3F",
        title_color="#9A9A9A",
        value_color="#FFFFFF",
        footer_color="#9A9A9A"
    )
    
    BLUE = CardTheme(
        background_color="#F4F9FE",
        separator_color="#E1E8ED",
        value_color="#1DC7EA"
    )