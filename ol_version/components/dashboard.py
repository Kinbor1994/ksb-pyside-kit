"""Dashboard module for handling the main application layout.

This module contains the Dashboard class which manages the overall layout including
sidebar, navbar, content area and footer.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict

from ..core.commons import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    Signal,
)
from .sidebar import SideBar, SideBarItem
from .contentarea import ContentArea
from .navbar import NavBar
from .footer import Footer
from .themes.dashboard import DashboardTheme, DashboardThemes

class Dashboard(QWidget):
    """Main dashboard widget with flexible sidebar, navbar, content and footer"""

    def __init__(
        self, 
        logo: Optional[QWidget] = None,
        collapsed_logo: Optional[QWidget] = None,
        menu_items: Optional[List[SideBarItem]] = None,
        theme: Optional[DashboardTheme] = None, 
        parent=None
    ):
        super().__init__(parent)
        self.setObjectName("dashboard")
        self.theme = theme or DashboardThemes.LIGHT
        
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Container pour sidebar et contenu principal
        self.container = QHBoxLayout()
        self.container.setContentsMargins(0, 0, 0, 0)
        self.container.setSpacing(0)

        # Sidebar avec menu items
        
        # Validate logo and collapsed_logo
        if (logo and not collapsed_logo) or (not logo and collapsed_logo):
            raise ValueError("Both logo and collapsed_logo must be provided together")
        
        self.sidebar = SideBar(logo=logo, collapsed_logo=collapsed_logo, theme=theme, menu_items=menu_items)
        self.container.addWidget(self.sidebar)

        # Layout contenu principal
        self.main_content = QVBoxLayout()
        self.main_content.setContentsMargins(0, 0, 0, 0)
        self.main_content.setSpacing(0)

        # Navbar
        self.navbar = NavBar()
        self.main_content.addWidget(self.navbar)

        # Zone de contenu
        self.content = ContentArea()
        self.main_content.addWidget(self.content)
    
        # Footer
        self.footer = Footer()
        self.main_content.addWidget(self.footer)

        # Ajouter le contenu principal au container
        self.container.addLayout(self.main_content)

        # Ajouter le container au layout principal
        self.layout.addLayout(self.container)

        # Connecter le signal du toggle sidebar
        self.navbar.toggle_sidebar.connect(self.toggle_sidebar)

        # État du sidebar
        self.sidebar_expanded = True

        # Connecter le signal de navigation du sidebar
        self.sidebar.page_changed.connect(self.navigate_to)
        self.content.page_not_found.connect(self.handle_page_not_found)
        
        # Appliquer le thème
        self.apply_theme()

    def add_page(self, route: str, page: QWidget):
        """Ajouter une page au dashboard
        
        Args:
            route: Route unique de la page
            page: Widget de la page à ajouter
        """
        self.content.add_page(route, page)

    def navigate_to(self, route: str):
        """Naviguer vers une page spécifique
        
        Args:
            route: Route de la page à afficher
        """
        self.content.show_page(route)

    def handle_page_not_found(self, route: str):
        """Gérer les erreurs de navigation
        
        Args:
            route: Route qui n'a pas été trouvée
        """
        print(f"Page non trouvée : {route}")  # TODO Handle error properly
        
    def toggle_sidebar(self):
        """Toggle sidebar expansion state"""
        self.sidebar_expanded = not self.sidebar_expanded
        self.sidebar.toggle_size(self.sidebar_expanded)

    def set_theme(self, theme: DashboardTheme):
        """
        Change the dashboard theme
        
        Args:
            theme: New theme to apply
        """
        self.theme = theme
        self.apply_theme()

    def apply_theme(self):
        """Apply the current theme to all components"""
        self.setStyleSheet(self.theme.get_stylesheet())

    def set_sidebar_menu(self, items: List[SideBarItem]):
        """
        Set sidebar menu items
        
        Args:
            items: List of menu items to set
        """
        self.sidebar.set_menu_items(items)

    def set_logo(self, expanded_logo: QWidget, collapsed_logo: QWidget):
        """
        Set sidebar logos for both states
        
        Args:
            expanded_logo: Logo to show when sidebar is expanded
            collapsed_logo: Logo to show when sidebar is collapsed
        """
        self.sidebar.set_logo(expanded_logo, collapsed_logo)