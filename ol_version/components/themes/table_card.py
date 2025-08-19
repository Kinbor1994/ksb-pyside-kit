"""Theme module for table cards.

This module provides theming capabilities specifically for table card widgets.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class TableCardTheme:
    """Theme configuration for table cards"""
    # Général
    background_color: str = "#FFFFFF"
    border_radius: int = 4
    border_color: str = "rgba(63,63,68,0.1)"
    padding: int = 15
    spacing: int = 10

    # Titre
    title_color: str = "#9A9A9A"
    title_font_size: int = 14

    # Table
    table_header_color: str = "#9A9A9A"
    table_header_background: str = "#FFFFFF"
    table_header_font_size: int = 12
    table_header_height: int = 40
    table_row_height: int = 35
    table_alternate_color: str = "rgba(63,63,68,0.05)"
    table_text_color: str = "#252422"
    table_text_font_size: int = 12
    table_hover_color: str = "rgba(29,199,234,0.1)"
    table_selected_color: str = "rgba(29,199,234,0.2)"
    
    # Séparateur
    separator_color: str = "#EEEEEE"
    separator_height: int = 1
    
    # Description (Footer)
    footer_color: str = "#9A9A9A"
    footer_font_size: int = 12

    def get_card_stylesheet(self) -> str:
        """Generate card stylesheet"""
        return f"""
            #baseCard {{
                background-color: {self.background_color};
                border-radius: {self.border_radius}px;
                border: 1px solid {self.border_color};
            }}
        """

    def get_table_stylesheet(self) -> str:
        """Génère le style spécifique pour la table"""
        return f"""
            QTableView {{
                border: none;
                background-color: {self.background_color};
                alternate-background-color: {self.table_alternate_color};
                gridline-color: {self.separator_color};
                color: {self.table_text_color};
                font-size: {self.table_text_font_size}px;
                outline: none;  /* Supprime la bordure de focus */
            }}
            
            QTableView::item {{
                padding: 8px;
                border: none;
                outline: none;  /* Supprime la bordure de focus sur les cellules */
            }}
            
            /* Style pour la ligne entière au survol */
            QTableView::item:hover {{
                background-color: {self.table_hover_color};
            }}
            
            /* Style pour la ligne sélectionnée */
            QTableView::item:selected {{
                background-color: {self.table_selected_color};
                color: {self.table_text_color};
                outline: none;  /* Supprime la bordure de focus sur la sélection */
            }}
            
            /* En-tête sans effet de survol */
            QHeaderView::section {{
                background-color: {self.table_header_background};
                color: {self.table_header_color};
                padding: 8px;
                border: none;
                border-bottom: 1px solid {self.separator_color};
                font-weight: bold;
                font-size: {self.table_header_font_size}px;
                height: {self.table_header_height}px;
                outline: none;  /* Supprime la bordure de focus sur les en-têtes */
            }}

            /* Supprime le focus sur le viewport de la table */
            QTableView QTableCornerButton::section {{
                background-color: {self.table_header_background};
                border: none;
                outline: none;
            }}
        """

class TableCardThemes:
    """Predefined table card themes"""
    
    LIGHT = TableCardTheme()
    
    DARK = TableCardTheme(
        background_color="#2C2C2C",
        border_color="#3F3F3F",
        title_color="#FFFFFF",
        table_header_color="#FFFFFF",
        table_header_background="#2C2C2C",
        table_text_color="#FFFFFF",
        table_alternate_color="rgba(255,255,255,0.05)",
        table_hover_color="rgba(29,199,234,0.2)",
        table_selected_color="rgba(29,199,234,0.3)",
        separator_color="#3F3F3F",
        footer_color="#9A9A9A"
    )
    
    BLUE = TableCardTheme(
        background_color="#F4F9FE",
        border_color="#E1E8ED",
        title_color="#1DC7EA",
        table_header_color="#1DC7EA",
        table_header_background="#F4F9FE",
        table_text_color="#252422",
        table_alternate_color="rgba(29,199,234,0.05)",
        table_hover_color="rgba(29,199,234,0.1)",
        table_selected_color="rgba(29,199,234,0.2)",
        separator_color="#E1E8ED",
        footer_color="#7A92A3"
    )