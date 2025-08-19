from dataclasses import dataclass, field
from typing import Optional, List, Tuple

from PySide6.QtCore import QPropertyAnimation, QEasingCurve

from ..core.commons import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QScrollArea,
    QSizePolicy,
    Qt,
    Signal,
)

from ..widgets.button import Button, IconButton
from ..core.themes.themes import ThemeManager,  ButtonTheme
from .themes.dashboard import DashboardTheme, DashboardThemes

@dataclass
class SideBarItem:
    """Configuration for sidebar menu items"""
    text: str
    icon: str
    route: Optional[str] = None 
    on_click: Optional[callable] = None
    tooltip: Optional[str] = None
    theme: Optional[ButtonTheme] = None
    subitems: List['SideBarItem'] = field(default_factory=list)
    is_expanded: bool = False


class SideBar(QFrame):
    """
    Flexible sidebar widget that supports expandable/collapsible menu items.
    """
    page_changed = Signal(str)
    
    def __init__(
        self,
        menu_items: Optional[List[SideBarItem]] = None,
        logo: Optional[QWidget] = None,
        collapsed_logo: Optional[QWidget] = None,
        collapsible: bool = True,
        theme: Optional[DashboardTheme] = None,
        parent=None
    ):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setMinimumWidth(70 if collapsible else 250)
        self.setMaximumWidth(250)
        
        self._theme = theme or DashboardThemes.LIGHT
        self.collapsible = collapsible
        self.expanded = True
        
        self.menu_items_widgets: List[Tuple[Button, List[Button]]] = []
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 0, 0, 0)
        self.layout.setSpacing(1)
        
        self.logo_widget = logo
        self.collapsed_logo = collapsed_logo
        
        self.setup_logo_area()
        self.setup_scroll_area()
        #self.setup_toggle_button()
        
        if menu_items:
            self.set_menu_items(menu_items)

    def setup_logo_area(self):
        """Initialize the logo container area"""
        self.logo_area = QWidget()
        self.logo_area.setFixedHeight(60)
        self.logo_layout = QHBoxLayout(self.logo_area)
        self.logo_layout.setContentsMargins(10, 10, 10, 0)
        
        if self.logo_widget:
            self.logo_layout.addWidget(self.logo_widget)
        if self.collapsed_logo:
            self.logo_layout.addWidget(self.collapsed_logo)
            self.collapsed_logo.hide()
        
        self.layout.addWidget(self.logo_area)

    def setup_scroll_area(self):
        """Initialize scroll area and menu container"""
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("sidebar-scroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.menu_area = QWidget()
        self.menu_layout = QVBoxLayout(self.menu_area)
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_layout.setSpacing(1)
        self.menu_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.menu_area)
        self.layout.addWidget(self.scroll_area, 1)
    
    def setup_toggle_button(self):
        """Button to toggle sidebar expansion"""
        if self.collapsible:
            self.toggle_button = IconButton(
                icon="fa5s.angle-double-left",
                on_click=self.toggle_sidebar,
                theme=ThemeManager.ButtonThemes.SECONDARY  
            )
            self.layout.addWidget(self.toggle_button)

    def set_menu_items(self, items: List[SideBarItem]):
        """Set all menu items at once"""
        self._clear_menu_items()
        for item in items:
            self.add_menu_item(item)

    def _clear_menu_items(self):
        """Remove all existing menu items"""
        for main_button, sub_buttons in self.menu_items_widgets:
            main_button.deleteLater()
            for sub_button in sub_buttons:
                sub_button.deleteLater()
        self.menu_items_widgets.clear()

    def add_menu_item(self, item: SideBarItem):
        """Add a menu item with optional subitems"""
        
        def create_click_handler(route: str):
            """Crée un gestionnaire de clic qui émet le signal avec la route"""
            return lambda: self.page_changed.emit(route)
        
        # Définir le gestionnaire de clic
        if item.route:
            on_click = create_click_handler(item.route)
        else:
            on_click = item.on_click
        
        main_button = Button(
            text=item.text if self.expanded else "",
            icon=item.icon,
            tooltip=item.tooltip,
            theme=self._theme.sidebar_item_theme,
            on_click=on_click if not item.subitems else lambda: self.toggle_subitems(main_button, item),
            width=230 if self.expanded else 60,
            height=45
        )
        
        self.menu_layout.addWidget(main_button)
        
        sub_buttons = []
        for subitem in item.subitems:
            # Définir le gestionnaire de clic pour le sous-élément
            if subitem.route:
                sub_on_click = create_click_handler(subitem.route)
            else:
                sub_on_click = subitem.on_click
                
            sub_button = Button(
                text=subitem.text,
                icon=subitem.icon,
                tooltip=subitem.tooltip, 
                theme=subitem.theme,  
                on_click=sub_on_click,
                width=210 if self.expanded else 55,
                height=40
            )
            sub_button.setVisible(False)
            self.menu_layout.addWidget(sub_button)
            sub_buttons.append(sub_button)
        
        self.menu_items_widgets.append((main_button, sub_buttons))
    
    def toggle_subitems(self, main_button: Button, item: SideBarItem):
        """Show or hide subitems when clicking the main button"""
        item.is_expanded = not item.is_expanded
        for button, sub_buttons in self.menu_items_widgets:
            if button == main_button:
                animation = QPropertyAnimation(button, b"minimumHeight")
                animation.setDuration(300)
                animation.setEasingCurve(QEasingCurve.InOutQuad)
                new_height = 45 + (40 * len(sub_buttons) if item.is_expanded else 0)
                animation.setEndValue(new_height)
                animation.start()
                for sub_button in sub_buttons:
                    sub_button.setVisible(item.is_expanded)
    
    def toggle_sidebar(self):
        """Collapse or expand the sidebar"""
        self.expanded = not self.expanded
        new_width = 265 if self.expanded else 70
        
        # Animation de la largeur
        animation = QPropertyAnimation(self, b"minimumWidth")
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.setEndValue(new_width)
        animation.start()
        
        # Mettre à jour l'interface
        self.update_buttons_visibility(self.expanded)
        self.update_logo(self.expanded)
    
    def update_buttons_visibility(self, is_expanded: bool):
        """
        Update visibility of all menu buttons based on sidebar state
        
        Args:
            is_expanded: True if sidebar is expanded, False if collapsed
        """
        for main_button, sub_buttons in self.menu_items_widgets:
            main_button._button.setFixedWidth(230 if is_expanded else 60)
            if not hasattr(main_button, '_original_text'):
                main_button._original_text = main_button._text
                
            # Restaurer le texte original ou le masquer selon l'état
            main_button.set_text(main_button._original_text if is_expanded else "")
            
            # Masquer les sous-boutons si le sidebar est replié
            for sub_button in sub_buttons:
                sub_button.setVisible(is_expanded and sub_button.isVisible())
                
    def update_logo(self, is_expanded: bool):
        """
        Update logo visibility based on sidebar state
        
        Args:
            is_expanded: True if sidebar is expanded, False if collapsed
        """
        if self.logo_widget and self.collapsed_logo:
            self.logo_widget.setVisible(is_expanded)
            self.collapsed_logo.setVisible(not is_expanded)

    def toggle_size(self, is_expanded: bool):
        """Handle sidebar size change"""
        width = 250 if is_expanded else 70
        self.setMinimumWidth(width)
        self.setMaximumWidth(width)
        
        self.update_buttons_visibility(is_expanded)
        self.update_logo(is_expanded)
