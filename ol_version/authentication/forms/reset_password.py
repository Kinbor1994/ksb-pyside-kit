from typing import Optional

from ..controllers.user_controller import AuthController
from ..models.user_model import UserModel
from ...core.commons import (
    QWidget,
    QDialog,
    QHBoxLayout,
    Qt,
    QVBoxLayout,
    QPoint,
    Signal
)
from ...widgets.text import Text
from ...widgets.text_field import PasswordField
from ...widgets.button import Button
from ...components.image_widget import ImageWidget

from ...widgets.themes.button_themes import ButtonThemes
from ...widgets.themes.text_themes import TextThemes
from ..themes.auth_forms_themes import FormTheme, FormThemes, FormType

class ResetPasswordForm(QDialog):
    """Formulaire de réinitialisation du mot de passe"""
    
    reset_success = Signal(object)
    reset_failed = Signal(str)
    
    def __init__(self, user: UserModel, theme: Optional[FormTheme] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self._dragging = False
        self._drag_position = QPoint()
        self.setObjectName("reset-password-form")
        self.setFixedWidth(800)
        
        self.user = user
        self.auth_controller = AuthController()
        self.theme = theme or FormThemes.LIGHT
        
        # Main layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Image section
        self.image_container = QWidget()
        self.image_container.setFixedWidth(400)
        self.image_container.setObjectName("image-container")
        self.image_layout = QVBoxLayout(self.image_container)
        self.image = ImageWidget(
            "ksb_pyside_kit/assets/reset_password.png",
            width=400,
            height=600,
            keep_aspect_ratio=True
        )
        self.image_layout.addWidget(self.image)
        self.main_layout.addWidget(self.image_container)
        
        # Form container
        self.form_container = QWidget()
        self.form_layout = QVBoxLayout(self.form_container)
        self.form_layout.setContentsMargins(30, 30, 30, 30)
        self.form_layout.setSpacing(20)
        
        # Title
        self.title = Text(
            value="Nouveau mot de passe",
            theme=TextThemes.H3_PRIMARY
        )
        self.form_layout.addWidget(self.title)
        
        # Password fields
        self.password_field = PasswordField(
            key="password",
            label="Nouveau mot de passe (*)",
            required=True,
            can_reveal_password=True,
            width=340,
            parent=self
        )
        self.form_layout.addWidget(self.password_field)
        
        self.confirm_password_field = PasswordField(
            key="confirm_password",
            label="Confirmer le mot de passe (*)",
            required=True,
            can_reveal_password=True,
            width=340,
            parent=self
        )
        self.form_layout.addWidget(self.confirm_password_field)
        
        # Buttons
        self.button_layout = QHBoxLayout()
        self.reset_button = Button(
            key="reset-btn",
            text="Réinitialiser",
            theme=ButtonThemes.PRIMARY,
            width=160,
            height=45,
            on_click=self.handle_reset
        )
        self.cancel_button = Button(
            key="cancel-btn",
            text="Fermer",
            theme=ButtonThemes.DANGER,
            width=160,
            height=45,
            on_click=self.close
        )
        self.button_layout.addWidget(self.reset_button)
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.setAlignment(Qt.AlignCenter)
        self.form_layout.addLayout(self.button_layout)
        
        # Error message
        self.error_message = Text(
            value="",
            theme=TextThemes.ERROR
        )
        self.error_message.hide()
        self.form_layout.addWidget(self.error_message)
        
        self.main_layout.addWidget(self.form_container)
        self.apply_theme()
        
    def handle_reset(self):
        """Gérer la réinitialisation du mot de passe"""
        if not self.password_field.is_valid() or not self.confirm_password_field.is_valid():
            return
            
        if self.password_field.value != self.confirm_password_field.value:
            self.show_error("Les mots de passe ne correspondent pas")
            return
            
        try:
            if self.auth_controller.change_password(
                user_id=self.user.id,
                new_password=self.password_field.value
            ):
                from .login import LoginForm
                login_form = LoginForm()
                login_form.show()
                self.close()
            else:
                self.show_error("Échec de la réinitialisation du mot de passe")
                
        except Exception as e:
            self.show_error(str(e))
            
    def show_error(self, message: str):
        self.error_message.setText(message)
        self.error_message.show()
        
    def apply_theme(self):
        self.setStyleSheet(self.theme.get_stylesheet(form_type=FormType.RESET_PASSWORD))

    # Mouse event handlers for window dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_position = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self._dragging:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = False
            event.accept()
