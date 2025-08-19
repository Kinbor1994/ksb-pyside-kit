from typing import Optional

from ..controllers.user_controller import AuthController
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
from ...widgets.text_field import TextField
from ...widgets.button import Button
from ...components.image_widget import ImageWidget

from ...widgets.themes.button_themes import ButtonThemes
from ...widgets.themes.text_themes import TextThemes
from ..themes.auth_forms_themes import FormTheme, FormThemes, FormType

class ForgotPasswordForm(QDialog):
    """
    Forgot password form step 1: Identifier verification
    """
    
    verify_success = Signal(object)  # Emits user object
    verify_failed = Signal(str)      # Emits error message
    show_login_form = Signal()       # Signal to switch back to login
    
    def __init__(self, theme: Optional[FormTheme] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self._dragging = False
        self._drag_position = QPoint()
        self.setObjectName("forgot-password-form")
        self.setFixedWidth(800)
        
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
            "ksb_pyside_kit/assets/forgot_password.png",
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
            value="Mot de passe oublié ?",
            theme=TextThemes.H3_PRIMARY
        )
        self.form_layout.addWidget(self.title)
        
        # Description
        self.description = Text(
            value="Entrez votre nom d'utilisateur ou email pour réinitialiser votre mot de passe",
            theme=TextThemes.LABEL_INFO_CENTER
        )
        self.form_layout.addWidget(self.description)
        
        # Identifier field
        self.identifier_field = TextField(
            key="identifier",
            label="Nom d'utilisateur ou Email (*)",
            required=True,
            hint_text="johndoe ou johndoe@example.com",
            width=340,
            parent=self
        )
        self.form_layout.addWidget(self.identifier_field)
        
        # Buttons
        self.button_layout = QHBoxLayout()
        self.verify_button = Button(
            key="verify-btn",
            text="Continuer",
            theme=ButtonThemes.PRIMARY,
            width=160,
            height=45,
            on_click=self.handle_verify
        )
        self.cancel_button = Button(
            key="cancel-btn",
            text="Fermer",
            theme=ButtonThemes.DANGER,
            width=160,
            height=45,
            on_click=self.switch_to_login
        )
        
        self.button_layout.addWidget(self.verify_button)
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
        self.setLayout(self.main_layout)
        
        # Apply theme
        self.apply_theme()
    
    def handle_verify(self):
        """Verify identifier and proceed to next step"""
        if not self.identifier_field.is_valid():
            return
            
        try:
            identifier = self.identifier_field.value
            user = None
            
            # Search by username or email
            if '@' in identifier:
                users = self.auth_controller.find_by_attributes(email=identifier)
            else:
                users = self.auth_controller.find_by_attributes(username=identifier)
                
            if users:
                user = users[0]
                self.verify_success.emit(user)
                # Transition to secret question form
                from .secret_question import SecretQuestionForm
                question_form = SecretQuestionForm(user=user)
                question_form.show()
                self.close()
            else:
                self.show_error("Aucun compte trouvé avec cet identifiant")
                
        except Exception as e:
            self.show_error(str(e))
            self.verify_failed.emit(str(e))
    
    def switch_to_login(self):
        """Return to login form"""
        self.show_login_form.emit()
        self.close()
    
    def show_error(self, message: str):
        """Display error message"""
        self.error_message.setText(message)
        self.error_message.show()
        
    def apply_theme(self):
        """Apply current theme to form"""
        self.setStyleSheet(self.theme.get_stylesheet(form_type=FormType.FORGOT_PASSWORD))

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
