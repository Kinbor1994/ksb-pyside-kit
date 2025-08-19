from dataclasses import dataclass

@dataclass
class FormTheme:
    """Theme configuration for forms"""
    # Main colors
    background_color: str = "#ffffff"
    image_background_color: str = "#f0f4f8" 
    text_color: str = "#2d3436"
    border_color: str = "#EAECEF"
    input_bg_color: str = "#FFFFFF"
    error_color: str = "#FA896B"

    def get_stylesheet(self) -> str:
        """Generate stylesheet for forms"""
        return f"""
            QWidget#auth-form {{
                background-color: {self.background_color};
                border-radius: 10px;
                border: 1px solid {self.border_color};
                padding: 30px;
            }}
            
            QWidget#image-container {{
                background-color: {self.image_background_color};
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
            }}
            
            QLabel {{
                color: {self.text_color};
            }}
            
        """

class FormThemes:
    """Predefined themes for forms"""
    
    LIGHT = FormTheme(
        background_color="#ffffff",
        image_background_color="#f0f4f8", 
        text_color="#2d3436",
        border_color="#EAECEF",
        input_bg_color="#FFFFFF",
        error_color="#FA896B"
    )
    
    DARK = FormTheme(
        background_color="#2A3447",
        image_background_color="#1F2833",  
        text_color="#ffffff",
        border_color="#3A445E",
        input_bg_color="#2A3447",
        error_color="#FA896B"
    )