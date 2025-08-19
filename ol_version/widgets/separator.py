from dataclasses import dataclass
from ..core.commons import QFrame
from ..core.themes.themes import ThemeManager, SeparatorTheme

class Separator(QFrame):
    """Widget de séparation horizontal ou vertical"""
    
    def __init__(
        self,
        orientation: str = "horizontal",
        theme: SeparatorTheme = None
    ):
        super().__init__()
        
        self._theme = theme or ThemeManager.SeparatorThemes.DEFAULT
        
        if orientation == "horizontal":
            self.setFrameShape(QFrame.HLine)
        else:
            self.setFrameShape(QFrame.VLine)
            
        self.setFrameShadow(QFrame.Sunken)
        self._apply_theme(self._theme)
        
    def _apply_theme(self, theme: SeparatorTheme) -> None:
        """Appliquer le thème au widget"""
        self.setStyleSheet(theme.get_stylesheet())