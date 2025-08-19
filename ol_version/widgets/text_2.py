from typing import Optional
from ..core.commons import QLabel, Qt, Signal, QFont, QMouseEvent, QHBoxLayout, QWidget
from .icon import Icon

class Text(QWidget):
    """A customizable text widget with optional icon support.
    
    Args:
        value (str): The text to display
        icon (Optional[str]): Icon name for QtAwesome (e.g., 'fa5s.user')
        icon_size (Optional[int]): Size of the icon in pixels
        icon_color (Optional[str]): Color of the icon
        font_size (Optional[int]): Font size of the text
        font_family (Optional[str]): Font family of the text
        font_weight (Optional[str]): Weight of the font (e.g., 'normal', 'bold')
        color (Optional[str]): Color of the text
        align (Optional[str]): Text alignment ('left', 'center', 'right')
        italic (Optional[bool]): Whether the text is italicized
        underline (Optional[bool]): Whether the text is underlined
        letter_spacing (Optional[int]): Spacing between letters
        line_height (Optional[float]): Line height multiplier
        selectable (Optional[bool]): Whether the text is selectable
        on_click (Optional[callable]): Function to call when clicked
    """
    
    clicked = Signal()

    def __init__(
        self,
        value: str = "",
        icon: Optional[str] = None,
        icon_size: Optional[int] = 16,
        icon_color: Optional[str] = None,
        font_size: Optional[int] = 14,
        font_family: Optional[str] = "Arial",
        font_weight: Optional[str] = "normal",
        color: Optional[str] = "black",
        align: Optional[str] = "left",
        italic: Optional[bool] = False,
        underline: Optional[bool] = False,
        letter_spacing: Optional[int] = 0,
        line_height: Optional[float] = 1.2,
        selectable: Optional[bool] = False,
        on_click: Optional[callable] = None,
        parent=None,
    ):
        super().__init__(parent)
        
        # Create layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        
        # Add icon if specified
        if icon:
            self.icon = Icon(
                icon=icon,
                size=icon_size,
                color=icon_color or color
            )
            self.layout.addWidget(self.icon)
        
        # Add text label
        self.label = QLabel(value)
        self.label.setFont(self._create_font(
            font_size, font_family, font_weight, italic, underline
        ))
        self.label.setStyleSheet(self._create_stylesheet(
            color, align, letter_spacing, line_height
        ))
        self.label.setAlignment(self._get_alignment(align))
        self.label.setTextInteractionFlags(
            Qt.TextSelectableByMouse if selectable else Qt.NoTextInteraction
        )
        self.layout.addWidget(self.label)
        self.layout.setStretch(1, 1)  # Allow label to expand
        self.layout.setStretch(0, 0)  # Icon should not expand
        
        if on_click:
            self.clicked.connect(on_click)

    def _create_font(self, size, family, weight, italic, underline) -> QFont:
        """Creates a QFont instance with the specified properties."""
        font = QFont(family, size)
        font.setItalic(italic)
        font.setUnderline(underline)
        font.setBold(weight.lower() == "bold")
        return font

    def _create_stylesheet(self, color, align, letter_spacing, line_height) -> str:
        """Creates a stylesheet for additional styling."""
        return f"""
        QLabel {{
            color: {color};
            letter-spacing: {letter_spacing}px;
            line-height: {line_height};
        }}
        """

    def _get_alignment(self, align: str) -> Qt.Alignment:
        """Converts alignment string to Qt alignment."""
        alignment_map = {
            "left": Qt.AlignLeft,
            "center": Qt.AlignCenter,
            "right": Qt.AlignRight,
        }
        return alignment_map.get(align.lower(), Qt.AlignLeft)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Emit the clicked signal when the widget is clicked."""
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            
    def setText(self, text: str):
        """Set the text of the label."""
        self.label.setText(text)
        
    def text(self) -> str:
        """Get the current text."""
        return self.label.text()