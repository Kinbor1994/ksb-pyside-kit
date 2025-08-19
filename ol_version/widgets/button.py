from typing import Optional, Callable, Any
from ..core.commons import Qt, QSize, QPushButton, QWidget

import qtawesome as qta

from ..core.base_widget import BaseWidget
from ..core.themes.themes import ThemeManager

class ButtonBase(BaseWidget):
    """
    Base class for all button widgets.
    
    This class provides common button functionality including:
    - Text and icon support
    - Click handling
    - Theme customization
    - State management

    Args:
        key (str, optional): Unique widget identifier
        width (int, optional): Button width
        height (int, optional): Button height
        tooltip (str, optional): Button tooltip
        visible (bool): Initial visibility state
        disabled (bool): Initial disabled state
        theme (ThemeManager): Button theme configuration
        parent (QWidget, optional): Parent widget
        
        text (str): Button text
        icon (str, optional): QtAwesome icon name
        icon_color (str, optional): Icon color
        on_click (callable, optional): Click event handler
        icon_size (int, optional): Size of the icon in pixels
        flat (bool): Whether the button should be flat
    """

    def __init__(
        self,
        key: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        tooltip: Optional[str] = None,
        visible: bool = True,
        disabled: bool = False,
        theme: ThemeManager = None,
        parent: Optional[QWidget] = None,
        #
        # ButtonBase specific
        #
        text: str = "",
        icon: Optional[str] = None,
        icon_color: Optional[str] = None,
        on_click: Optional[Callable] = None,
        icon_size: int = 24,
        flat: bool = False,
    ) -> None:
        # Store button specific attributes
        self._text = text
        self._icon = icon
        self._icon_color = icon_color
        self._icon_size = icon_size
        self._flat = flat
        self.on_click = on_click

        # Initialize base widget
        super().__init__(
            key=key,
            width=width,
            height=height,
            tooltip=tooltip,
            visible=visible,
            disabled=disabled,
            theme=theme,
            parent=parent,
        )

    def _setup_ui(self) -> None:
        """
        Initialize button UI elements
        """
        
        # Create main button
        self._button = QPushButton(self._text, self)
        self._button.setCursor(Qt.PointingHandCursor)
        self._button.setFlat(self._flat)
        self._button.setFixedSize(self._width, self._height)
        self._button.setEnabled(not self._disabled) 
        self._button.setVisible(self._visible)
        # Setup icon if specified
        if self._icon:
            self._setup_icon()
        
        # Add button to the main layout (inherited from BaseWidget)
        self.main_layout.addWidget(self._button)

    def _setup_icon(self) -> None:
        """Set up button icon."""
        try:
            icon = qta.icon(self._icon, color=self._icon_color)
            self._button.setIcon(icon)
            self._button.setIconSize(QSize(self._icon_size, self._icon_size))
        except Exception as e:
            print(f"Error loading icon '{self._icon}': {e}")

    def _setup_signals(self) -> None:
        """Connect button signals."""
        if self.on_click:
            self._button.clicked.connect(self.on_click)

    # Helper methods
    def set_text(self, text: str) -> None:
        """Set button text."""
        self._text = text
        if hasattr(self, '_button'):
            self._button.setText(text)

    def set_icon(self, icon_name: str, color: Optional[str] = None) -> None:
        """Set button icon."""
        self._icon = icon_name
        self._icon_color = color or self._icon_color
        if hasattr(self, '_button'):
            self._setup_icon()

    def click(self) -> None:
        """Programmatically trigger button click."""
        if hasattr(self, '_button') and self._button.isEnabled():
            self._button.click()
            
class Button(ButtonBase):
    """
    A standard button with text and optional icon support.
    
    Args:
        text (str): Button text content
        icon (str, optional): QtAwesome icon name (e.g. 'fa5s.save')
        icon_color (str, optional): Color for the icon. Defaults to "white"
        on_click (callable, optional): Function to call when button is clicked
        key (str, optional): Unique widget identifier
        width (int, optional): Button width in pixels. Defaults to 150
        height (int, optional): Button height in pixels. Defaults to 50
        tooltip (str, optional): Tooltip text shown on hover
        visible (bool): Initial visibility state. Defaults to True
        disabled (bool): Initial disabled state. Defaults to False
        theme (ThemeManager): Button theme configuration
        parent (QWidget, optional): Parent widget
    
    Example:
        ```python
        save_btn = Button(
            text="Sauvegarder",
            icon="fa5s.save",
            key="save_button",
            theme=ThemeManager.ButtonThemes.PRIMARY,
            on_click=lambda: print("Sauvegarde!")
        )
        ```
    """

    def __init__(
        self,
        text: str,
        icon: Optional[str] = None,
        icon_color: str = "white",
        on_click: Optional[Callable] = None,
        key: Optional[str] = None,
        width: int = 150,
        height: int = 50,
        tooltip: Optional[str] = None,
        visible: bool = True,
        disabled: bool = False,
        theme: ThemeManager = ThemeManager.ButtonThemes.PRIMARY,
        parent = None,
    ) -> None:
        super().__init__(
            key=key,
            width=width,
            height=height,
            tooltip=tooltip,
            visible=visible,
            disabled=disabled,
            theme=theme,
            parent=parent,
            text=text,
            icon=icon,
            icon_color=icon_color,
            on_click=on_click
        )

class IconButton(ButtonBase):
    """
    A button that displays only an icon.
    
    Args:
        icon (str): QtAwesome icon name (e.g. 'fa5s.cog')
        icon_color (str, optional): Color for the icon. Defaults to "white"
        on_click (callable, optional): Function to call when button is clicked
        key (str, optional): Unique widget identifier
        width (int, optional): Button width in pixels. Defaults to 150
        height (int, optional): Button height in pixels. Defaults to 50
        size (int, optional): Button width and height in pixels. Defaults to 45
        tooltip (str, optional): Tooltip text shown on hover
        visible (bool): Initial visibility state. Defaults to True
        disabled (bool): Initial disabled state. Defaults to False
        theme (ThemeManager): Button theme configuration
        parent (QWidget, optional): Parent widget
    
    Example:
        ```python
        settings_btn = IconButton(
            icon="fa5s.cog",
            tooltip="Paramètres",
            theme=ThemeManager.ButtonThemes.SECONDARY,
            on_click=lambda: print("Configuration!")
        )
        ```
    """

    def __init__(
        self,
        icon: str,
        icon_color: str = "white",
        on_click: Optional[Callable] = None,
        key: Optional[str] = None,
        width: Optional[int] = 45,
        height: Optional[int] = 45,
        tooltip: Optional[str] = None,
        visible: bool = True,
        disabled: bool = False,
        theme: ThemeManager = ThemeManager.ButtonThemes.PRIMARY,
        parent = None,
    ) -> None:
        super().__init__(
            key=key,
            width=width,
            height=height,
            tooltip=tooltip,
            visible=visible,
            disabled=disabled,
            theme=theme,
            parent=parent,
            text="",
            icon=icon,
            icon_color=icon_color,
            on_click=on_click
        )

class TextButton(ButtonBase):
    """
    A flat button that displays only text.
    
    Args:
        text (str): Button text content
        on_click (callable, optional): Function to call when button is clicked
        key (str, optional): Unique widget identifier
        width (int, optional): Button width in pixels. Defaults to None (auto)
        height (int, optional): Button height in pixels. Defaults to None (auto)
        tooltip (str, optional): Tooltip text shown on hover
        visible (bool): Initial visibility state. Defaults to True
        disabled (bool): Initial disabled state. Defaults to False
        theme (ThemeManager): Button theme configuration
        parent (QWidget, optional): Parent widget
    
    Example:
        ```python
        link_btn = TextButton(
            text="En savoir plus",
            theme=ThemeManager.ButtonThemes.LINK,
            on_click=lambda: print("Plus d'informations")
        )
        ```
    """

    def __init__(
        self,
        text: str,
        on_click: Optional[Callable] = None,
        key: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        tooltip: Optional[str] = None,
        visible: bool = True,
        disabled: bool = False,
        theme: ThemeManager = ThemeManager.ButtonThemes.PRIMARY,
        parent = None,
    ) -> None:
        super().__init__(
            key=key,
            width=width,
            height=height,
            tooltip=tooltip,
            visible=visible,
            disabled=disabled,
            theme=theme,
            parent=parent,
            text=text,
            flat=True,
            on_click=on_click
        )