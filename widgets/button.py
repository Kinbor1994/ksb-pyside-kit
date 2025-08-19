"""
Modern Button widget implementation with Pydantic configuration.
"""

from typing import Optional
import logging
from core.qt_imports import QPushButton, QHBoxLayout, Qt, QSize, QIcon, QWidget
import qtawesome as qta

from ..core.base_widgets import BaseWidget, WidgetFactory
from ..core.models import ButtonConfig, BaseWidgetConfig, ThemeConfig, Size, AlignmentEnum

logger = logging.getLogger(__name__)

class ButtonWidget(BaseWidget[ButtonConfig]):
    """
    Modern button widget with comprehensive configuration support.
    
    Features:
    - Text and icon support with flexible positioning
    - Multiple button variants (primary, secondary, etc.)
    - Hover and active state animations
    - Checkable button support
    - Comprehensive event handling
    
    Example:
        ```python
        config = ButtonConfig(
            text="Save Document",
            icon="fa5s.save",
            style=theme.get_widget_style("button", "primary")
        )
        button = ButtonWidget(config=config, theme=theme)
        ```
    """
    
    def __init__(
        self,
        config: Optional[ButtonConfig] = None,
        theme: Optional[ThemeConfig] = None,
        parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(config, theme, parent)
        
        # Connect button-specific signals
        if self._button and self._config.on_click:
            self._button.clicked.connect(self._config.on_click)
        
        if self._button and self._config.on_toggle:
            self._button.toggled.connect(self._config.on_toggle)
    
    def _get_default_config(self) -> ButtonConfig:
        """Get default button configuration."""
        return ButtonConfig(
            text="Button",
            width=Size.px(120),
            height=Size.px(40)
        )
    
    def _setup_layout(self) -> None:
        """Setup button layout and create button widget."""
        super()._setup_layout()
        
        # Create button layout
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create QPushButton
        self._button = QPushButton()
        self._button.setCursor(Qt.PointingHandCursor)
        
        # Configure button properties
        self._configure_button()
        
        # Add button to layout
        self.button_layout.addWidget(self._button)
        self.main_layout.addLayout(self.button_layout)
    
    def _configure_button(self) -> None:
        """Configure button properties from configuration."""
        # Set text
        if self._config.text:
            self._button.setText(self._config.text)
        
        # Set icon
        if self._config.icon:
            self._setup_icon()
        
        # Set size
        if self._config.width and self._config.height:
            self._button.setFixedSize(
                int(self._config.width.value),
                int(self._config.height.value)
            )
        
        # Set checkable state
        self._button.setCheckable(self._config.checkable)
        self._button.setChecked(self._config.checked)
        
        # Set flat style
        self._button.setFlat(self._config.flat)
        
        # Set as default button
        self._button.setDefault(self._config.default)
    
    def _setup_icon(self) -> None:
        """Setup button icon."""
        try:
            icon = qta.icon(self._config.icon)
            self._button.setIcon(icon)
            
            icon_size = int(self._config.icon_size.value)
            self._button.setIconSize(QSize(icon_size, icon_size))
            
        except Exception as e:
            logger.error(f"Error setting up icon '{self._config.icon}': {e}")
    
    def _apply_config_changes(self, old_config: ButtonConfig, new_config: ButtonConfig) -> None:
        """Apply button-specific configuration changes."""
        super()._apply_config_changes(old_config, new_config)
        
        # Update text
        if old_config.text != new_config.text:
            self._button.setText(new_config.text)
        
        # Update icon
        if old_config.icon != new_config.icon:
            if new_config.icon:
                self._setup_icon()
            else:
                self._button.setIcon(QIcon())
        
        # Update checkable state
        if old_config.checkable != new_config.checkable:
            self._button.setCheckable(new_config.checkable)
        
        if old_config.checked != new_config.checked:
            self._button.setChecked(new_config.checked)
    
    def click(self) -> None:
        """Programmatically trigger button click."""
        if self._button.isEnabled():
            self._button.click()
    
    def set_text(self, text: str) -> None:
        """Update button text."""
        config_dict = self._config.dict()
        config_dict['text'] = text
        self.apply_config(ButtonConfig(**config_dict))
    
    def set_icon(self, icon: str) -> None:
        """Update button icon."""
        config_dict = self._config.dict()
        config_dict['icon'] = icon
        self.apply_config(ButtonConfig(**config_dict))
    
    @property
    def is_checked(self) -> bool:
        """Get button checked state."""
        return self._button.isChecked()
    
    @is_checked.setter
    def is_checked(self, checked: bool) -> None:
        """Set button checked state."""
        self._button.setChecked(checked)


# Register button widget
WidgetFactory.register("button", ButtonWidget)