from typing import Optional

from ..controllers.user_controller import AuthController
from ..models.user_model import UserType
from ...core.commons import (
    QWidget,
    QDialog,
    QHBoxLayout,
    Qt,
    QCheckBox,
    QFormLayout,
    QVBoxLayout,
    QPoint,
    Signal
)
from ...widgets.text import Text
from ...widgets.text_field import TextField, EmailField, PasswordField
from ...widgets.button import Button
from ...widgets.combobox import ComboBox
from ...components.image_widget import ImageWidget

from ...widgets.themes.button_themes import ButtonTheme, ButtonThemes
from ...widgets.themes.text_themes import TextTheme, TextThemes
from ..themes.auth_forms_themes import FormTheme, FormThemes, FormType

class LoginForm(QDialog):
    """
    Login form widget for authentication.
    
    Signals:
        auth_success (UserModel): Emitted when authentication succeeds
        auth_failed (str): Emitted when authentication fails with error message
        show_register_form (): Emitted to switch to the registration form
    """
    
    auth_success = Signal(object)  # Emits UserModel instance
    auth_failed = Signal(str)      # Emits error message
    show_register_form = Signal()  # Signal pour afficher le formulaire d'inscription
    
    def __init__(self, theme: Optional[FormTheme] = None,  parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self._dragging = False
        self._drag_position = QPoint()
        self.setObjectName("auth-form")
        self.setFixedWidth(800)  # Augmenter la largeur pour accommoder l'image
        
        # Initialize controller
        self.auth_controller = AuthController()
        self.theme = theme or FormThemes.LIGHT
        
        # Main layout horizontal
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Image section
        self.image_container = QWidget()
        self.image_container.setFixedWidth(400)
        self.image_container.setObjectName("image-container")
        self.image_layout = QVBoxLayout(self.image_container)
        self.login_image = ImageWidget(
            "ksb_pyside_kit/assets/login.png",
            width=400,
            height=600,
            keep_aspect_ratio=True
        )
        self.image_layout.addWidget(self.login_image)
        self.main_layout.addWidget(self.image_container)
        
        # Form container
        self.form_container = QWidget()
        self.form_layout = QVBoxLayout(self.form_container)
        self.form_layout.setContentsMargins(30, 30, 30, 30)
        self.form_layout.setSpacing(20)
        
        # Welcome text
        self.welcome_label = Text(value="Authentification!", theme=TextThemes.H3_PRIMARY)
        self.form_layout.addWidget(self.welcome_label)
        
        # Username field
        self.username_field = TextField(
            key="username",
            label="Nom d'utilisateur (*)",
            required=True,
            hint_text="johndoe",
            width=340,
            parent=self,
        )
        self.form_layout.addWidget(self.username_field)
        
        # Password field
        self.password_field = PasswordField(
            key="password",
            label="Mot de passe (*)", 
            required=True,
            hint_text="••••••••",
            can_reveal_password=True,
            width=340,
            parent=self,
        )
        self.form_layout.addWidget(self.password_field)
        
        # Remember me and Forgot password row
        self.options_layout = QHBoxLayout()
        

        self.forgot_password_link = Text(
            value="Mot de passe oublé?",
            theme=TextThemes.LINK,
            on_click=lambda: print("Forgot password link clicked"),
        )
        self.options_layout.addWidget(self.forgot_password_link, alignment=Qt.AlignRight)
        
        self.form_layout.addLayout(self.options_layout)
        
        self.button_layout = QHBoxLayout()
        # Login button
        self.login_button = Button(
            key="login-btn",
            text="Se connecter",
            theme=ButtonThemes.PRIMARY,
            width=160,
            height=45,
            on_click=self.handle_login
        )
        self.cancel_button = Button(
            key="cancel-btn",
            text="Fermer",
            theme=ButtonThemes.DANGER,
            width=160,
            height=45,
            on_click=self.close
        )
        
        self.button_layout.addWidget(self.login_button)
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.setAlignment(Qt.AlignCenter)
        self.button_layout.setSpacing(10)
        self.button_layout.addStretch(1)
        self.form_layout.addLayout(self.button_layout)
        # Error message
        self.error_message = Text(
            value="",
            theme=TextThemes.ERROR,
        )
        self.error_message.setObjectName("error-message")
        self.error_message.hide()
        self.form_layout.addWidget(self.error_message)
        
        # Sign up text
        self.signup_layout = QHBoxLayout()
        self.signup_text = Text(value="Pass encore inscrit?", theme=TextThemes.LABEL_PRIMARY_CENTER)
        self.signup_link = Text(
            value="Créer un compte",
            theme=TextThemes.LINK,
            on_click=self.switch_to_register
        )
        self.signup_layout.addWidget(self.signup_text)
        self.signup_layout.addWidget(self.signup_link)
        self.signup_layout.setAlignment(Qt.AlignCenter)
        self.form_layout.addLayout(self.signup_layout)
        
        self.main_layout.addWidget(self.form_container)
        
        self.setLayout(self.main_layout)
        
        # Connect signal to handler
        self.show_register_form.connect(self.show_register_form_handler)
        
        # Apply theme
        self.apply_theme()
    
    def handle_login(self):
        """Handle login attempt"""
        # Validate fields
        if not self.username_field.is_valid() or not self.password_field.is_valid():
            return
            
        try:
            # Attempt authentication
            success, user = self.auth_controller.authenticate(
                username=self.username_field.value,
                password=self.password_field.value
            )
            
            if success:
                # Clear form and emit success signal
                self.clear_form()
                self.error_message.hide()
                self.auth_success.emit(user)
            else:
                # Show error
                self.show_error("Nom d'utilisateur ou mot de passe invalide")
                self.auth_failed.emit("Authentication failed")
                
        except Exception as e:
            self.show_error(str(e))
            self.auth_failed.emit(str(e))
    
    def show_error(self, message: str):
        """Display error message"""
        self.error_message.setText(message)
        self.error_message.show()
    
    def clear_form(self):
        """Reset form to initial state"""
        self.username_field.clear_content()
        self.password_field.clear_content()
        self.error_message.hide()
    
    def apply_theme(self):
        """Apply current theme to form"""
        self.setStyleSheet(self.theme.get_stylesheet(form_type=FormType.LOGIN)) 

    def switch_to_register(self):
        """Gérer la transition vers le formulaire d'inscription"""
        self.show_register_form.emit()
        # Ne pas fermer tout de suite, le gestionnaire de signal s'en chargera

    def show_register_form_handler(self):
        """Gestionnaire appelé lorsque le signal show_register_form est émis"""
        from .signup import RegisterForm  # Import local pour éviter les imports circulaires
        register_form = RegisterForm()
        register_form.show_login_form.connect(self.show_login_form_handler)
        register_form.show()
        self.close()

    @classmethod
    def show_login_form_handler(cls, theme=None, on_forgot_password=None):
        """Méthode de classe pour créer et afficher le formulaire de connexion"""
        login_form = cls(theme=theme, on_forgot_password=on_forgot_password)
        login_form.show()
        return login_form

    def mousePressEvent(self, event):
        """Gérer le clic de souris pour commencer le déplacement"""
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_position = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        """Gérer le déplacement de la fenêtre"""
        if event.buttons() & Qt.LeftButton and self._dragging:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Gérer le relâchement du clic pour arrêter le déplacement"""
        if event.button() == Qt.LeftButton:
            self._dragging = False
            event.accept()