from dataclasses import dataclass

@dataclass
class ImageTheme:
    """Thème pour le widget ImageWidget"""
    background_color: str = "transparent"
    border_radius: int = 10
    border_color: str = "transparent"
    border_width: int = 0
    padding: int = 0
    shadow_color: str = "transparent"
    shadow_radius: int = 0

    def get_stylesheet(self) -> str:
        """Génère le style CSS pour le widget"""
        return f"""
            QLabel#image-widget {{
                background-color: {self.background_color};
                border-radius: {self.border_radius}px;
                border: {self.border_width}px solid {self.border_color};
                padding: {self.padding}px;
            }}
            
            QLabel#image-widget[class="with-shadow"] {{
                background-color: {self.background_color};
                border-radius: {self.border_radius}px;
                border: {self.border_width}px solid {self.border_color};
                padding: {self.padding}px;
                margin: {self.shadow_radius}px;
            }}
        """

class ImageThemes:
    """Thèmes prédéfinis pour le widget ImageWidget"""
    
    TRANSPARENT = ImageTheme()
    
    CARD = ImageTheme(
        background_color="#ffffff",
        border_radius=10,
        border_color="#EAECEF",
        border_width=1,
        padding=10
    )
    
    SHADOW = ImageTheme(
        background_color="#ffffff",
        border_radius=10,
        shadow_color="#0000001A",
        shadow_radius=20,
        padding=10
    )