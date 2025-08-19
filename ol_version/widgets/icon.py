from typing import Optional
import qtawesome as qta
from ..core.commons import QLabel, Qt

class Icon(QLabel):
    """A customizable icon widget using QtAwesome.
    
    Args:
        icon (str): The icon name (e.g., 'fa5s.user')
        size (Optional[int]): Size of the icon in pixels
        color (Optional[str]): Color of the icon (e.g., 'red', '#FF5733')
        parent: Parent widget
    """
    
    def __init__(
        self,
        icon: str,
        size: Optional[int] = 16,
        color: Optional[str] = "black",
        parent=None
    ):
        super().__init__(parent)
        
        # Create QtAwesome icon
        qta_icon = qta.icon(icon, color=color)
        
        # Set pixmap with desired size
        self.setPixmap(qta_icon.pixmap(size, size))
        
        # Center align the icon
        self.setAlignment(Qt.AlignCenter)