from typing import Optional, Callable
from ..core.commons import QLabel, Qt, Signal, QFont, QMouseEvent, QHBoxLayout
from ..core.base_widget import BaseWidget
from .icon import Icon
from ..core.themes.themes import ThemeManager, TextTheme

class Text(BaseWidget):
    """
    A customizable text widget with optional icon support.
    
    This widget provides:
    - Text display with customizable font and style
    - Optional icon support
    - Click handling
    - Theme customization
    - Text selection support
    - Alignment options
    
    Signals:
        clicked: Emitted when the text is clicked
        
    Properties:
        value (str): The displayed text content
        theme (TextTheme): Current text theme
        alignment (str): Current text alignment
        
    Args:
        value (str): The text to display
        icon (str, optional): QtAwesome icon name (e.g., 'fa5s.user')
        icon_size (int, optional): Icon size in pixels. Defaults to 16
        icon_color (str, optional): Icon color. If not set, uses theme color
        theme (ThemeManager): Theme for styling. Defaults to ThemeManager.TextThemes.DEFAULT
        selectable (bool): Whether text can be selected. Defaults to False
        on_click (callable, optional): Click event handler
        align (str, optional): Text alignment ('left', 'center', 'right')
        key (str, optional): Unique widget identifier
        width (int, optional): Widget width in pixels
        height (int, optional): Widget height in pixels
        tooltip (str, optional): Hover tooltip text
        visible (bool): Initial visibility state. Defaults to True
        disabled (bool): Initial disabled state. Defaults to False
        parent (QWidget, optional): Parent widget
        
    Example:
        ```python
        text = Text(
            value="Hello World",
            icon="fa5s.info-circle",
            theme=ThemeManager.TextThemes.HEADING,
            on_click=lambda: print("Text clicked!")
        )
        ```
    """
    
    clicked = Signal()

    def __init__(
        self,
        value: str = "",
        icon: Optional[str] = None,
        icon_size: int = 16,
        icon_color: Optional[str] = None,
        theme: TextTheme = ThemeManager.TextThemes.DEFAULT,
        selectable: bool = False,
        on_click: Optional[Callable] = None,
        align: Optional[str] = None,
        key: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = 20,
        tooltip: Optional[str] = None,
        visible: bool = True,
        disabled: bool = False,
        parent = None,
    ) -> None:
        # Store text specific attributes
        self._text = value
        self._icon_name = icon
        self._icon_size = icon_size
        self._icon_color = icon_color
        self._text_theme = theme
        self._selectable = selectable
        self._text_align = align or theme.align
        
        # Initialize base widget
        super().__init__(
            key=key,
            width=width,
            height=height,
            tooltip=tooltip,
            visible=visible,
            disabled=disabled,
            theme=None,
            parent=parent
        )
        
        # Connect click handler if provided
        if on_click:
            self.clicked.connect(on_click)

        
            
    def _setup_ui(self,) -> None:
        """Set up the text widget UI elements."""
        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(1)
    
        # Add icon if specified
        if self._icon_name:
            self._setup_icon()
        
        # Add text label
        self._setup_label()

    def _setup_icon(self) -> None:
        """Set up the icon widget if specified."""
        self.icon = Icon(
            icon=self._icon_name,
            size=self._icon_size,
            color=self._icon_color
        )
        self.content_layout.addWidget(self.icon)

    def _setup_label(self) -> None:
        """Set up the text label with current theme and settings."""
        self.label = QLabel(self._text)
        
        if self._width:
            self.setMinimumWidth(self._width)
            
        # Apply theme and alignment
        if self._text_align:
            self._text_theme = self._text_theme.with_modifications(
                align=self._text_align
            )
            
        self._apply_theme(self._text_theme)
        self.label.setAlignment(self._get_alignment(self._text_theme.align))
        
        # Configure text selection
        self.label.setTextInteractionFlags(
            Qt.TextSelectableByMouse if self._selectable else Qt.NoTextInteraction
        )
        
        self.content_layout.addWidget(self.label)
        self.content_layout.setStretch(1, 1)  # Allow label to expand
        self.content_layout.setStretch(0, 0)  # Icon should not expand
        self.main_layout.addLayout(self.content_layout)

    def _apply_theme(self, theme: ThemeManager) -> None:
        """Apply theme to the text label."""
        self._text_theme = theme
        if hasattr(self, 'label'):
            self.label.setStyleSheet(theme.get_stylesheet())
            self.label.setFont(self._create_font(theme))

    def _create_font(self, theme: ThemeManager) -> QFont:
        """Create a QFont instance from theme properties."""
        font = QFont(theme.font_family, theme.font_size)
        font.setItalic(theme.italic)
        font.setUnderline(theme.underline)
        font.setBold(theme.font_weight.lower() == "bold")
        return font

    def _get_alignment(self, align: str) -> Qt.Alignment:
        """Convert alignment string to Qt alignment constant."""
        alignment_map = {
            "left": Qt.AlignLeft,
            "center": Qt.AlignCenter,
            "right": Qt.AlignRight,
        }
        return alignment_map.get(align.lower(), Qt.AlignLeft)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release events for click detection."""
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    # Public API
    @property
    def text(self) -> str:
        """Get current text content."""
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        """Set text content."""
        self._text = value
        if hasattr(self, 'label'):
            self.label.setText(value)
            
    @property
    def theme(self) -> ThemeManager:
        """Get current text theme."""
        return self._text_theme

    @theme.setter
    def theme(self, value: ThemeManager) -> None:
        """Set text theme."""
        self._apply_theme(value)
            
    @property
    def alignment(self) -> str:
        """Get current text alignment."""
        return self._text_align

    @alignment.setter
    def alignment(self, value: str) -> None:
        """Set text alignment."""
        if value not in ("left", "center", "right"):
            raise ValueError("Alignment must be 'left', 'center' or 'right'")
            
        self._text_align = value
        self._text_theme = self._text_theme.with_modifications(align=value)
        self._apply_theme(self._text_theme)
        if hasattr(self, 'label'):
            self.label.setAlignment(self._get_alignment(value))