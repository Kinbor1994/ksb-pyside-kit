from typing import Dict

from ..core.commons import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    Signal,
    QStackedWidget,
    QScrollArea,
    Qt,
)
from ..widgets.text import Text
from ..core.themes.themes import TextTheme, ThemeManager

class Page(QWidget):
    """Base class for all dashboard pages
    
    This class provides a standard structure and lifecycle methods for dashboard pages.
    Each page consists of a header with a title and a content area that can be customized.
    
    Args:
        title (str): The page title displayed in the header
        parent (QWidget, optional): The parent widget. Defaults to None.
    """
    
    def __init__(self, title: str="", parent=None):
        super().__init__(parent)
        self.title = title
        self.is_loaded = False
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)
        self.setLayout(self.main_layout)
        
        # Initialize header and content areas
        self.setup_header()
        
        # Main content area
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.content)
        
        # Setup page specific content
        self.setup_content()
        
    def setup_header(self):
        """Initialize the page header with title"""
        self.header = QHBoxLayout()
        self.header.setContentsMargins(0, 0, 0, 5)
        
        # Page title
        if self.title:
            self.title_label = Text(
                value=self.title,
                theme=ThemeManager.TextThemes.H1
            )
            self.header.addWidget(self.title_label)
            
            # Add header to main layout
            self.main_layout.addLayout(self.header)
    
    def setup_content(self):
        """Override this method to initialize page specific content
        
        This method is called during initialization and should be used
        to create and setup all widgets specific to this page.
        """
        pass
    
    def on_show(self):
        """Called when the page becomes visible
        
        Handles initial data loading if needed and refreshes the page content.
        """
        if not self.is_loaded:
            self.load_data()
            self.is_loaded = True
        self.refresh_data()
    
    def on_hide(self):
        """Called when the page is hidden
        
        Used to save page state and perform cleanup if needed.
        """
        self.save_state()
    
    def load_data(self):
        """Load initial page data
        
        Override this method to perform initial data loading
        when the page is shown for the first time.
        """
        pass
    
    def refresh_data(self):
        """Refresh page data
        
        Override this method to update page content with fresh data.
        Called every time the page becomes visible.
        """
        pass
    
    def save_state(self):
        """Save page state
        
        Override this method to save any page state that needs
        to be preserved when the page is hidden.
        """
        pass
    
    def set_loading(self, loading: bool):
        """Set the loading state of the page
        
        Args:
            loading (bool): True to show loading state, False to hide it
        """
        self.content.setEnabled(not loading)
    
    def show_error(self, message: str):
        """Display an error message using themed text

        Args:
            message (str): The error message to display
        """
        error_text = Text(
            value=message,
            align="center",
            theme=ThemeManager.TextThemes.ERROR
        )
        self.content_layout.addWidget(error_text)
    
    def clear(self):
        """Clear all content from the page
        
        Removes all widgets from the content area.
        """
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

class ContentArea(QFrame):
    """Widget pour la zone de contenu avec gestion des pages"""
    page_not_found = Signal(str)  # Nouveau signal pour les erreurs
    page_changed = Signal(str)    # Signal pour notifier du changement de page

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("content")
        
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)
        self.setLayout(self.main_layout)

        # Création du QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container pour le contenu défilable
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        
        # Gestionnaire de pages
        self.pages = QStackedWidget()
        self.scroll_layout.addWidget(self.pages)
        
        # Configuration du scroll area
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)
        
        # Dictionnaire pour stocker les routes des pages
        self.routes: Dict[str, int] = {}
        
    def add_page(self, route: str, page: QWidget):
        """Ajouter une nouvelle page
        
        Args:
            route: Route unique pour accéder à la page
            page: Widget de la page à ajouter
        """
        index = self.pages.addWidget(page)
        self.routes[route] = index
        
    def show_page(self, route: str):
        """Afficher une page spécifique
        
        Args:
            route: Route de la page à afficher
        """
        if route in self.routes:
            current_widget = self.pages.currentWidget()
            if hasattr(current_widget, 'on_hide'):
                current_widget.on_hide()
                
            self.pages.setCurrentIndex(self.routes[route])
            
            new_widget = self.pages.currentWidget()
            if hasattr(new_widget, 'on_show'):
                new_widget.on_show()
                
            self.page_changed.emit(route)
        else:
            self.page_not_found.emit(route)