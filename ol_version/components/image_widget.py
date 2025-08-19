from typing import Optional

from ..core.commons import QWidget, QLabel, Qt, QPixmap, QImage

from .themes.image_widget_theme import ImageTheme, ImageThemes

class ImageWidget(QLabel):
    def __init__(
        self,
        image_path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        keep_aspect_ratio: bool = True,
        theme: Optional[ImageTheme] = None,
        parent=None
    ):
        super().__init__(parent)
        self.setObjectName("image-widget")
        
        self._image_path = image_path
        self._keep_aspect_ratio = keep_aspect_ratio
        self._width = width
        self._height = height
        self._theme = theme or ImageThemes.TRANSPARENT
        
        # Appliquer le thème
        self.apply_theme()
        
        # Chargement de l'image
        self._pixmap = QPixmap(image_path)
        if not self._pixmap.isNull():
            self._setup_image()
        else:
            raise(f"Erreur: Impossible de charger l'image: {image_path}")
    
    def apply_theme(self):
        """Applique le thème au widget"""
        if self._theme:
            self.setStyleSheet(self._theme.get_stylesheet())
            if self._theme.shadow_radius > 0:
                self.setProperty("class", "with-shadow")
    
    def set_theme(self, theme: ImageTheme):
        """Change le thème du widget"""
        self._theme = theme
        self.apply_theme()
        
    def _setup_image(self):
        """Configure l'affichage de l'image"""
        if self._width and self._height:
            if self._keep_aspect_ratio:
                self._pixmap = self._pixmap.scaled(
                    self._width,
                    self._height,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            else:
                self._pixmap = self._pixmap.scaled(
                    self._width,
                    self._height,
                    Qt.IgnoreAspectRatio,
                    Qt.SmoothTransformation
                )
        
        self.setPixmap(self._pixmap)
        
    def set_image(self, image_path: str):
        """Change l'image affichée"""
        self._image_path = image_path
        self._pixmap = QPixmap(image_path)
        if not self._pixmap.isNull():
            self._setup_image()
            
    def resize_image(self, width: int, height: int):
        """Redimensionne l'image"""
        self._width = width
        self._height = height
        self._setup_image()

    def set_keep_aspect_ratio(self, keep_aspect_ratio: bool):
        """Définit si le ratio d'aspect doit être conservé"""
        self._keep_aspect_ratio = keep_aspect_ratio
        self._setup_image()