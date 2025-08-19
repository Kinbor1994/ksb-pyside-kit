from typing import Optional
from .commons import QWidget, QVBoxLayout

from .themes.themes import ThemeManager

class BaseWidget(QWidget):
    """
    Root base class for all widgets in the application.
    Provides the most basic common functionality.
        
    Args:
        key (str, optional): Unique identifier for the widget
        width (int, optional): Widget width in pixels
        height (int, optional): Widget height in pixels
        tooltip (str, optional): Hover tooltip text
        visible (bool, optional): Initial visibility state. Defaults to True
        disabled (bool, optional): Initial disabled state. Defaults to False
        theme (Any, optional): Theme configuration to apply
        parent (QWidget, optional): Parent widget. Defaults to None
    """

    def __init__(
        self,
        key: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        tooltip: Optional[str] = None,
        visible: bool = True,
        disabled: bool = False,
        theme: Optional[ThemeManager] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the base widget with common functionality."""
        super().__init__(parent)
        
        # Store instance attributes
        self._key = key
        self._width = width
        self._height = height
        self._tooltip = tooltip
        self._visible = visible
        self._disabled = disabled
        
        # Internal state
        self._theme = theme
        
        # Set object name if key provided
        if key:
            self.setObjectName(key)
        
        # Setup default layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(2)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Initialize widget
        self._setup_ui()
        self._setup_signals()
        self.apply_theme(self._theme)

    def _setup_ui(self) -> None:
        """
        Set up the widget's UI elements and properties.
        
        This method should be overridden by derived classes to add
        specific UI elements.
        """
        pass

    def _setup_signals(self) -> None:
        """
        Set up signal connections.
        
        This method should be overridden by derived classes to connect
        their specific signals.
        """
        pass

    def apply_theme(self, theme: ThemeManager) -> None:
        """
        Apply a theme to the widget.
        
        Args:
            theme: Theme configuration to apply
        """
        if theme and hasattr(theme, 'get_stylesheet'):
            self.setStyleSheet(theme.get_stylesheet())
            self._theme = theme

