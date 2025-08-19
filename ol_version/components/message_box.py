from typing import Optional, List, Tuple
from enum import Enum

from ..core.commons import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame, 
    QGraphicsDropShadowEffect,Qt, Signal, QMouseEvent
)

from ..widgets.text import Text
from ..widgets.button import Button
from ..core.themes.themes import ThemeManager, MessageBoxTheme
from ..widgets.separator import Separator
from ..widgets.icon import Icon


class MessageType(Enum):
    """Enumeration for different message types with corresponding styling."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    QUESTION = "question"


class MessageBoxResult(Enum):
    """Enumeration for possible message box results."""
    OK = "ok"
    CANCEL = "cancel"
    YES = "yes"
    NO = "no"
    RETRY = "retry"
    ABORT = "abort"
    CUSTOM = "custom"  # For custom button results


class MessageBox(QDialog):
    """Boîte de dialogue personnalisée avec support des thèmes."""
    
    buttonClicked = Signal(MessageBoxResult)

    def __init__(
        self,
        title: str,
        message: str,
        message_type: MessageType = MessageType.INFO,
        buttons: List[Tuple[str, MessageBoxResult]] = None,
        default_button: Optional[MessageBoxResult] = None,
        parent=None,
        theme: Optional[MessageBoxTheme] = None,
    ):
        super().__init__(parent)
        
        self.title = title
        self.message = message
        self.message_type = message_type
        self.buttons = buttons or [("OK", MessageBoxResult.OK)]
        self.default_button = default_button or self.buttons[0][1]
        self.theme = theme or ThemeManager.MessageBoxThemes.DEFAULT
        self._result = None
        
        # Configuration fenêtre
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.setMinimumSize(self.theme.min_width, self.theme.min_height)
        
        self._drag_position = None
        self._setup_ui()
        self._apply_theme()

    def _setup_ui(self):
        """Configuration de l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Frame principale
        self.frame = QFrame()
        self.frame.setObjectName("messageBoxFrame")
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(24, 24, 24, 24)
        
        # Ombre
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(self.theme.shadow_blur)
        shadow.setXOffset(self.theme.shadow_spread)
        shadow.setYOffset(self.theme.shadow_spread)
        self.frame.setGraphicsEffect(shadow)
        
        # Titre
        self.title_label = Text(
            value=self.title,
            theme=ThemeManager.TextThemes.H3
        )
        frame_layout.addWidget(self.title_label)
        
        # Séparateur
        self.separator = Separator(orientation="horizontal")
        frame_layout.addWidget(self.separator)
        
        # Layout pour l'icône et le message
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)  # Espacement entre l'icône et le message
        
        # Icône selon le type
        icon_name = {
            MessageType.INFO: "fa5s.info-circle",
            MessageType.SUCCESS: "fa5s.check-circle",
            MessageType.WARNING: "fa5s.exclamation-triangle",
            MessageType.ERROR: "fa5s.times-circle",
            MessageType.QUESTION: "fa5s.question-circle"
        }.get(self.message_type)
        
        #couleur de l'icône
        icon_color = {  
            MessageType.INFO: "#1DC7EA",
            MessageType.SUCCESS: "green",
            MessageType.WARNING: "#FFC107",
            MessageType.ERROR: "#DC3545",
            MessageType.QUESTION: "#1DC7EA",
        }.get(self.message_type)
        
        if icon_name:
            self.icon = Icon(icon=icon_name, color=icon_color, size=40)
            self.icon.setFixedSize(40, 40)  # Taille fixe pour l'icône
            content_layout.addWidget(self.icon)
        
        # Message (prendra tout l'espace disponible)
        self.message_label = Text(
            value=self.message,
            theme=ThemeManager.TextThemes.BODY
        )
        self.message_label.label.setWordWrap(True)
        content_layout.addWidget(self.message_label, 1)  # stretch factor = 1
        
        frame_layout.addLayout(content_layout)
        frame_layout.addStretch(1)
        
        # Boutons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(self.theme.button_spacing)
        button_layout.addStretch(1)
        
        for text, result in self.buttons:
            def create_click_handler(r):
                return lambda: self._handle_button_click(r)
            
            button = Button(
                text=text,
                theme=self._get_button_theme(result),
                on_click=create_click_handler(result)  
            )

            if result == self.default_button:
                button.setFocus()
            button_layout.addWidget(button)
        
        frame_layout.addLayout(button_layout)
        layout.addWidget(self.frame)

    def _get_button_theme(self, result: MessageBoxResult):
        """Retourne le thème approprié pour le bouton."""
        if result == MessageBoxResult.YES:
            return ThemeManager.ButtonThemes.PRIMARY
        elif result == MessageBoxResult.NO:
            return ThemeManager.ButtonThemes.DANGER
        return ThemeManager.ButtonThemes.SECONDARY

    def _handle_button_click(self, result: MessageBoxResult):
        """Gère le clic sur un bouton."""
        self._result = result
        self.buttonClicked.emit(result)
        self.accept()

    def _apply_theme(self):
        """Applique le thème."""
        self.setStyleSheet(self.theme.get_stylesheet())

    # Événements de déplacement de fenêtre
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton and self._drag_position:
            self.move(event.globalPosition().toPoint() - self._drag_position)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_position = None

    # Méthodes statiques utilitaires
    @staticmethod
    def show_info(title: str, message: str, parent=None) -> MessageBoxResult:
        dlg = MessageBox(
            title=title,
            message=message,
            message_type=MessageType.INFO,
            theme=ThemeManager.MessageBoxThemes.DEFAULT,
            parent=parent
        )
        dlg.exec()
        return dlg._result

    @staticmethod
    def show_success(title: str, message: str, parent=None) -> MessageBoxResult:
        dlg = MessageBox(
            title=title,
            message=message,
            message_type=MessageType.SUCCESS,
            theme=ThemeManager.MessageBoxThemes.SUCCESS,
            parent=parent
        )
        dlg.exec()
        return dlg._result

    @staticmethod
    def show_warning(title: str, message: str, parent=None) -> MessageBoxResult:
        dlg = MessageBox(
            title=title,
            message=message,
            message_type=MessageType.WARNING,
            theme=ThemeManager.MessageBoxThemes.WARNING,
            parent=parent
        )
        dlg.exec()
        return dlg._result

    @staticmethod
    def show_error(title: str, message: str, parent=None) -> MessageBoxResult:
        dlg = MessageBox(
            title=title,
            message=message,
            message_type=MessageType.ERROR,
            theme=ThemeManager.MessageBoxThemes.ERROR,
            parent=parent
        )
        dlg.exec()
        return dlg._result

    @staticmethod
    def show_confirm(
        title: str,
        message: str,
        parent=None,
        yes_text: str = "Oui",
        no_text: str = "Non"
    ) -> MessageBoxResult:
        dlg = MessageBox(
            title=title,
            message=message,
            message_type=MessageType.QUESTION,
            buttons=[(yes_text, MessageBoxResult.YES), (no_text, MessageBoxResult.NO)],
            theme=ThemeManager.MessageBoxThemes.QUESTION,
            parent=parent
        )
        dlg.exec()
        return dlg._result