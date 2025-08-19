from dataclasses import dataclass

@dataclass
class FormTheme:
    """Theme configuration for forms"""
    # Main colors
    background_color: str = "#ffffff"
    text_color: str = "#2d3436"

    def get_stylesheet(self) -> str:
        """Generate stylesheet for forms"""
        return f"""
            QWidget#auth-form {{
                background-color: {self.background_color};
            }}
        """

class FormThemes:
    """Predefined themes for forms"""
    
    LIGHT = FormTheme(
        background_color="#ffffff",
        text_color="#2d3436",
    )
    
    DARK = FormTheme(
        background_color="#1a1a1a",
        text_color="#ffffff",
    )
    
    BLUE = FormTheme(
        background_color="#f0f7ff",
        text_color="#1e3799",
    )