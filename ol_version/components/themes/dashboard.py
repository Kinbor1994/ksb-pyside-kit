from dataclasses import dataclass
from ...core.themes.themes import ButtonTheme

@dataclass
class DashboardTheme:
    """Theme configuration for Dashboard"""
    # Main colors
    background_color: str = "#f5f6fa"
    
    # Sidebar
    sidebar_background: str = "#2f3640"
    sidebar_text_color: str = "#ffffff"
    sidebar_hover_background: str = "#353b48"
    sidebar_active_background: str = "#40739e"
    sidebar_border: str = "none"
    sidebar_button_padding: str = "10px 15px"
    sidebar_scrollbar_width: str = "8px"
    sidebar_scrollbar_background: str = "transparent"
    sidebar_scrollbar_handle_color: str = "rgba(255, 255, 255, 0.2)"
    sidebar_scrollbar_handle_hover_color: str = "rgba(255, 255, 255, 0.3)"
    sidebar_scrollbar_radius: str = "4px"
    sidebar_item_spacing: str = "1px"
    sidebar_item_theme: ButtonTheme = None
    
    # Content Area
    content_background: str = "transparent"
    content_padding: str = "10px"
    content_spacing: str = "20px"
    content_scrollbar_width: str = "8px"
    content_scrollbar_background: str = "#F1F1F1"
    content_scrollbar_handle_color: str = "#C1C1C1"
    content_scrollbar_handle_hover_color: str = "#A8A8A8"
    content_scrollbar_handle_min_height: str = "30px"
    content_scrollbar_radius: str = "4px"
    
    # Navbar
    navbar_background: str = "white"
    navbar_text_color: str = "#2f3640"
    navbar_border_color: str = "#dcdde1"
    navbar_height: str = "60px"
    navbar_padding: str = "10px"
    
    # Footer
    footer_background: str = "white"
    footer_text_color: str = "#666666"
    footer_border_color: str = "#dcdde1"
    footer_height: str = "40px"
    footer_padding: str = "10px"
    
    def get_stylesheet(self) -> str:
        """Generate QSS stylesheet from theme settings"""
        return f"""
            #dashboard {{
                background-color: {self.background_color};
            }}
            
            /* Sidebar Styles */
            #sidebar {{
                background-color: {self.sidebar_background};
                border: {self.sidebar_border};
            }}
            
            #sidebar QPushButton {{
                color: {self.sidebar_text_color};
                text-align: left;
                padding: {self.sidebar_button_padding};
                border: none;
                border-radius: 0;
            }}
            
            #sidebar QPushButton:hover {{
                background-color: {self.sidebar_hover_background};
            }}
            
            #sidebar QPushButton:checked {{
                background-color: {self.sidebar_active_background};
            }}

            /* Sidebar Scroll Area */
            #sidebar-scroll {{
                background-color: {self.sidebar_background};
                border: none;
            }}
            
            #sidebar-scroll QWidget {{
                background-color: {self.sidebar_background};
            }}
            
            #sidebar-scroll QScrollBar:vertical {{
                width: {self.sidebar_scrollbar_width};
                background: {self.sidebar_background};
                margin: 0px;
                border: none;
            }}
        
            /* Sidebar Scrollbar */
            #sidebar QScrollBar:vertical {{
                width: {self.sidebar_scrollbar_width};
                background: {self.sidebar_background};
                margin: 0px;
                border: none;
            }}

            #sidebar QScrollBar::handle:vertical {{
                background: {self.sidebar_scrollbar_handle_color};
                border-radius: {self.sidebar_scrollbar_radius};
                min-height: 30px;
            }}
            
            #sidebar QScrollBar::handle:vertical:hover {{
                background: {self.sidebar_scrollbar_handle_hover_color};
            }}

            #sidebar QScrollBar::add-line:vertical,
            #sidebar QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
                border: none;
            }}

            #sidebar QScrollBar::add-page:vertical,
            #sidebar QScrollBar::sub-page:vertical {{
                background: {self.sidebar_background};
            }}
            
            /* Main Content */
            #content {{
                background-color: {self.content_background};
                padding: {self.content_padding};
            }}
            
            #content QScrollArea {{
                background-color: {self.content_background};
                border: none;
            }}
            
            #content QScrollArea > QWidget {{
                background-color: {self.content_background};
            }}
            
            #content QScrollArea QWidget {{
                background-color: {self.content_background};
            }}

            #content QScrollBar:vertical {{
                width: {self.content_scrollbar_width};
                background: {self.content_scrollbar_background};
                margin: 0px;
                border: none;
            }}
            
            #content QScrollBar::handle:vertical {{
                background: {self.content_scrollbar_handle_color};
                min-height: {self.content_scrollbar_handle_min_height};
                border-radius: {self.content_scrollbar_radius};
            }}
            
            #content QScrollBar::handle:vertical:hover {{
                background: {self.content_scrollbar_handle_hover_color};
            }}
            
            #content QScrollBar::add-line:vertical,
            #content QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            
            #content QScrollBar::add-page:vertical,
            #content QScrollBar::sub-page:vertical {{
                background: {self.content_scrollbar_background};
            }}
            
            #content QScrollBar:horizontal {{
                height: {self.content_scrollbar_width};
                background: {self.content_scrollbar_background};
                margin: 0px;
                border: none;
            }}
            
            #content QScrollBar::handle:horizontal {{
                background: {self.content_scrollbar_handle_color};
                min-width: {self.content_scrollbar_handle_min_height};
                border-radius: {self.content_scrollbar_radius};
            }}
            
            #content QScrollBar::handle:horizontal:hover {{
                background: {self.content_scrollbar_handle_hover_color};
            }}
            
            #content QScrollBar::add-line:horizontal,
            #content QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
                width: 0px;
            }}
            
            #content QScrollBar::add-page:horizontal,
            #content QScrollBar::sub-page:horizontal {{
                background: {self.content_scrollbar_background};
            }}
            
            #sidebar QScrollBar:horizontal {{
                height: {self.sidebar_scrollbar_width};
                background: {self.sidebar_background};
                margin: 0px;
                border: none;
            }}

            #sidebar QScrollBar::handle:horizontal {{
                background: {self.sidebar_scrollbar_handle_color};
                border-radius: {self.sidebar_scrollbar_radius};
                min-width: 30px;
            }}
            
            #sidebar QScrollBar::handle:horizontal:hover {{
                background: {self.sidebar_scrollbar_handle_hover_color};
            }}

            #sidebar QScrollBar::add-line:horizontal,
            #sidebar QScrollBar::sub-line:horizontal {{
                width: 0px;
                background: none;
                border: none;
            }}

            #sidebar QScrollBar::add-page:horizontal,
            #sidebar QScrollBar::sub-page:horizontal {{
                background: {self.sidebar_background};
            }}
            
            /* Navbar */
            #navbar {{
                background-color: {self.navbar_background};
                color: {self.navbar_text_color};
                border-bottom: 1px solid {self.navbar_border_color};
                min-height: {self.navbar_height};
                max-height: {self.navbar_height};
                padding: {self.navbar_padding};
            }}
            
            /* Footer */
            #footer {{
                background-color: {self.footer_background};
                color: {self.footer_text_color};
                border-top: 1px solid {self.footer_border_color};
                min-height: {self.footer_height};
                max-height: {self.footer_height};
                padding: {self.footer_padding};
            }}
        """
        
class DashboardThemes:
    """Predefined themes for Dashboard"""
    
    LIGHT = DashboardTheme(
        # Main colors
        background_color="#ffffff",
        
        # Sidebar - légèrement vert comme Brevo
        sidebar_background="#f5f9f6",  # Blanc avec une teinte verte légère
        sidebar_text_color="#2c3e50",  # Couleur de texte foncée
        sidebar_hover_background="#e8f3eb",  # Un peu plus vert au survol
        sidebar_active_background="#d7eadd",  # Encore plus vert pour l'élément actif
        sidebar_border="none",
        sidebar_button_padding="10px 15px",
        sidebar_item_spacing="1px",
        
        sidebar_item_theme=ButtonTheme(
            background_color="transparent",
            text_color="#2c3e50",  # Couleur de texte foncée assortie
            border_color="transparent",
            hover_background="#e8f3eb",  # Un peu plus vert au survol
            hover_border_color="transparent",
            pressed_background="#d7eadd",  # Encore plus vert quand pressé
            pressed_border_color="transparent",
            font_size=14,
            font_weight="bold",
            border_radius=6,
            disabled_opacity=0.65,
        ),
        
        # Sidebar Scrollbar
        sidebar_scrollbar_width="8px",
        sidebar_scrollbar_background="transparent",
        sidebar_scrollbar_handle_color="rgba(44, 62, 80, 0.2)",  # Couleur foncée transparente
        sidebar_scrollbar_handle_hover_color="rgba(44, 62, 80, 0.3)",  # Un peu plus foncée au survol
        sidebar_scrollbar_radius="4px",
        
        # Navbar
        navbar_background="white",
        navbar_text_color="#2f3640",
        navbar_border_color="#dcdde1",
        navbar_height="60px",
        navbar_padding="10px",
        
        
        content_background="transparent",
        content_padding="20px",
        content_spacing="20px",
        
        # Content Scrollbar
        content_scrollbar_width="8px",
        content_scrollbar_background="#F1F1F1",
        content_scrollbar_handle_color="#C1C1C1",
        content_scrollbar_handle_hover_color="#A8A8A8",
        content_scrollbar_handle_min_height="30px",
        content_scrollbar_radius="4px",
        
        # Footer
        footer_background="white",
        footer_text_color="#666666",
        footer_border_color="#dcdde1",
        footer_height="40px",
        footer_padding="10px"
    )
    
    DARK = DashboardTheme(
        # Main colors
        background_color="#ffffff",
        
        # Sidebar
        sidebar_background="#2f3640",
        sidebar_text_color="#ffffff",
        sidebar_hover_background="#353b48",
        sidebar_active_background="#40739e",
        sidebar_border="none",
        sidebar_button_padding="10px 15px",
        sidebar_item_spacing="1px",
        
        sidebar_item_theme=ButtonTheme(
            background_color="transparent",
            text_color="#ffffff",  # Couleur de texte blanc
            border_color="transparent",
            hover_background="#353b48",  # Couleur de survol
            hover_border_color="transparent",
            pressed_background="#40739e",  # Couleur quand pressé
            pressed_border_color="transparent",
            font_size=14,
            font_weight="bold",
            border_radius=6,
            disabled_opacity=0.65,
        ),
        
        # Sidebar Scrollbar
        sidebar_scrollbar_width="8px",
        sidebar_scrollbar_background="transparent",
        sidebar_scrollbar_handle_color="rgba(255, 255, 255, 0.2)",
        sidebar_scrollbar_handle_hover_color="rgba(255, 255, 255, 0.3)",
        sidebar_scrollbar_radius="4px",
        
        # Navbar
        navbar_background="white",
        navbar_text_color="#2f3640",
        navbar_border_color="#dcdde1",
        navbar_height="60px",
        navbar_padding="10px",
        

        content_background="transparent",
        content_padding="10px",
        content_spacing="5px",
        
        # Content Scrollbar
        content_scrollbar_width="8px",
        content_scrollbar_background="#F1F1F1",
        content_scrollbar_handle_color="#C1C1C1",
        content_scrollbar_handle_hover_color="#A8A8A8",
        content_scrollbar_handle_min_height="30px",
        content_scrollbar_radius="4px",
        
        # Footer
        footer_background="white",
        footer_text_color="#666666",
        footer_border_color="#dcdde1",
        footer_height="40px",
        footer_padding="10px"
    )

    BLUE = DashboardTheme(  
        # Main colors
        background_color="#ffffff",  # Modifié pour être blanc
        
        # Sidebar
        sidebar_background="#1e3799",
        sidebar_text_color="#ffffff",
        sidebar_hover_background="#2850a7",
        sidebar_active_background="#4a69bd",
        sidebar_border="none",
        sidebar_button_padding="10px 15px",
        sidebar_item_spacing="1px",
        
        sidebar_item_theme=ButtonTheme(
            background_color="transparent",
            text_color="#ffffff",  # Couleur de texte blanc
            border_color="transparent",
            hover_background="#2850a7",  # Couleur de survol
            hover_border_color="transparent",  
            pressed_background="#4a69bd",  # Couleur quand pressé
            pressed_border_color="transparent",
            font_size=16,
            font_weight="bold",
            border_radius=6,
            disabled_opacity=0.65,
        ),
        
        # Sidebar Scrollbar
        sidebar_scrollbar_width="8px",
        sidebar_scrollbar_background="transparent",
        sidebar_scrollbar_handle_color="rgba(255, 255, 255, 0.2)",
        sidebar_scrollbar_handle_hover_color="rgba(255, 255, 255, 0.3)",
        sidebar_scrollbar_radius="4px",
        
        # Navbar
        navbar_background="#1e3799",  # Modifié pour correspondre à la sidebar
        navbar_text_color="#ffffff",  # Texte blanc pour contraster
        navbar_border_color="#2850a7",
        navbar_height="60px",
        navbar_padding="10px",
        
        # Content Area
        content_background="transparent",
        content_padding="20px",
        content_spacing="20px",
        
        # Content Scrollbar
        content_scrollbar_width="8px", 
        content_scrollbar_background="#E6F0FF",
        content_scrollbar_handle_color="#B3D1FF",
        content_scrollbar_handle_hover_color="#80B3FF",
        content_scrollbar_handle_min_height="30px",
        content_scrollbar_radius="4px",
        
        # Footer
        footer_background="#1e3799",  # Modifié pour correspondre à la sidebar
        footer_text_color="#ffffff",  # Texte blanc pour contraster
        footer_border_color="#2850a7",
        footer_height="40px",
        footer_padding="10px"
    )

    GREEN = DashboardTheme(
        # Main colors
        background_color="#ffffff",  # Modifié pour être blanc
        
        # Sidebar
        sidebar_background="#2ecc71",
        sidebar_text_color="#ffffff",
        sidebar_hover_background="#27ae60",
        sidebar_active_background="#27ae60",
        sidebar_border="none",
        sidebar_button_padding="10px 15px",
        sidebar_item_spacing="1px",
        
        sidebar_item_theme=ButtonTheme(
            background_color="transparent",
            text_color="#ffffff",  # Couleur de texte blanc
            border_color="transparent",
            hover_background="#27ae60",  # Couleur de survol
            hover_border_color="transparent",
            pressed_background="#27ae60",  # Couleur quand pressé
            pressed_border_color="transparent",
            font_size=16,
            font_weight="bold",
            border_radius=6,
            disabled_opacity=0.65,
        ),
        # Sidebar Scrollbar
        sidebar_scrollbar_width="8px",
        sidebar_scrollbar_background="transparent",
        sidebar_scrollbar_handle_color="rgba(255, 255, 255, 0.2)",
        sidebar_scrollbar_handle_hover_color="rgba(255, 255, 255, 0.3)",
        sidebar_scrollbar_radius="4px",
        
        # Navbar
        navbar_background="#2ecc71",  # Modifié pour correspondre à la sidebar
        navbar_text_color="#ffffff",  # Texte blanc pour contraster
        navbar_border_color="#27ae60",
        navbar_height="60px",
        navbar_padding="10px",
        
        # Content Area
        content_background="transparent",
        content_padding="20px",
        content_spacing="20px",
        
        # Content Scrollbar
        content_scrollbar_width="8px",
        content_scrollbar_background="#E8F8E8",
        content_scrollbar_handle_color="#B3E6B3",
        content_scrollbar_handle_hover_color="#80CC80",
        content_scrollbar_handle_min_height="30px",
        content_scrollbar_radius="4px",
        
        # Footer
        footer_background="#2ecc71",  # Modifié pour correspondre à la sidebar
        footer_text_color="#ffffff",  # Texte blanc pour contraster
        footer_border_color="#27ae60",
        footer_height="40px",
        footer_padding="10px"
    )