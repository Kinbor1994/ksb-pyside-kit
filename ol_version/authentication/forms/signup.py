from typing import Optional

from ..controllers.user_controller import AuthController
from ..models.user_model import UserType, UserModel
from ..controllers.registration_code_controller import RegistrationCodeController
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

class RegisterForm(QDialog):
    """
    Register form widget for authentication.
    
    Signals:
        auth_success (UserModel): Emitted when authentication succeeds
        auth_failed (str): Emitted when authentication fails with error message
        show_login_form (): Emitted to switch to login form
    """
    
    register_success = Signal(object)  
    register_failed = Signal(str)      # Emits error message
    show_login_form = Signal()         # Signal to show login form
    
    def __init__(self, theme: Optional[FormTheme] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self._dragging = False
        self._drag_position = QPoint()
        self.setObjectName("register-form")
        self.setFixedWidth(900)  
        
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
            "ksb_pyside_kit/assets/signup.png",
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
        self.form_layout.setSpacing(5)
        
        # Welcome text
        self.welcome_label = Text(value="Inscription!", theme=TextThemes.H3_PRIMARY)
        self.form_layout.addWidget(self.welcome_label)
        
        self.username_layout = QHBoxLayout()
        self.username_layout.setSpacing(10)
        
        # Username field
        self.username_field = TextField(
            key="username",
            label="Nom d'utilisateur (*)",
            required=True,
            hint_text="johndoe",
            width=210,
            parent=self,
        )
        self.username_layout.addWidget(self.username_field)
        
        # Email field
        self.email_field = EmailField(
            key="email",
            label="Email (*)",
            required=True,
            hint_text="johndoe@example.com",
            width=210,
            parent=self,
        )
        self.username_layout.addWidget(self.email_field)
        self.username_layout.addStretch(1)
        self.form_layout.addLayout(self.username_layout)
        
        # Registration code field
        self.registration_code_field = TextField(
            key="registration_code",
            label="Code d'inscription (*)",
            required=True,
            hint_text="Entrez le code fourni",
            width=430,
            parent=self,
        )
        self.form_layout.addWidget(self.registration_code_field)
        
        # Secret question field
        questions = UserModel.secret_question.info["choices"]
        self.secret_question_field = ComboBox(
            key="secret_question",
            label="Question secrète (*)",
            required=True,
            options=questions,
            width=430,
            parent=self
        )
        self.form_layout.addWidget(self.secret_question_field)
        
        # Secret answer field
        self.secret_answer_field = TextField(
            key="secret_answer",
            label="Réponse secrète (*)",
            required=True,
            hint_text="Votre réponse",
            width=430,
            parent=self
        )
        self.form_layout.addWidget(self.secret_answer_field)
        
        self.password_layout = QHBoxLayout()
        self.password_layout.setSpacing(10)
        # Password field
        self.password_field = PasswordField(
            key="password",
            label="Mot de passe (*)", 
            required=True,
            hint_text="••••••••",
            can_reveal_password=True,
            width=210,
            parent=self,
        )
        self.password_layout.addWidget(self.password_field)
        
        # Confirm Password field
        self.confirme_password_field = PasswordField(
            key="confirm_password",
            label="Confirmer mot de passe (*)", 
            required=True,
            hint_text="••••••••",
            can_reveal_password=True,
            width=210,
            parent=self,
        )
        self.password_layout.addWidget(self.confirme_password_field)
        self.password_layout.addStretch(1)
        self.form_layout.addLayout(self.password_layout)
        
        self.button_layout = QHBoxLayout()
        # Login button
        self.signup_button = Button(
            key="signup-btn",
            text="S'inscrire",
            theme=ButtonThemes.PRIMARY,
            width=160,
            height=45,
            on_click=self.handle_register
        )
        self.cancel_button = Button(
            key="cancel-btn",
            text="Fermer",
            theme=ButtonThemes.DANGER,
            width=160,
            height=45,
            on_click=self.close
        )
        
        self.button_layout.addWidget(self.signup_button)
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.setAlignment(Qt.AlignCenter)
        self.button_layout.setSpacing(10)
        self.button_layout.addStretch(1)
        self.form_layout.addLayout(self.button_layout)
        # Error message
        self.error_message = Text(
            value="",
            theme=TextThemes.LABEL_NB,
        )
        self.error_message.hide()
        self.form_layout.addWidget(self.error_message)
        
        #NB Message
        self.nb_message = Text(
            value="Les champs marqués d'un (*) sont obligatoires",
            theme=TextThemes.LABEL_NB,
        )
        self.form_layout.addWidget(self.nb_message)
        
        # Sign up text
        self.login_layout = QHBoxLayout()
        self.login_text = Text(value="Déjà inscrit?", theme=TextThemes.LABEL_PRIMARY_CENTER)
        self.login_link = Text(
            value="Connecter vous",
            theme=TextThemes.LINK,
            on_click=self.switch_to_login
        )
        self.login_layout.addWidget(self.login_text)
        self.login_layout.addWidget(self.login_link)
        self.login_layout.setAlignment(Qt.AlignCenter)
        self.form_layout.addLayout(self.login_layout)
        self.form_layout.addStretch(1)
        self.main_layout.addWidget(self.form_container)
        
        self.setLayout(self.main_layout)
        
        # Connect signal to handler
        self.show_login_form.connect(self.show_login_form_handler)
        
        # Apply theme
        self.apply_theme()
    
    def switch_to_login(self):
        """Gérer la transition vers le formulaire de connexion"""
        self.show_login_form.emit()
        # Ne pas fermer tout de suite, le gestionnaire de signal s'en chargera

    def show_login_form_handler(self):
        """Gestionnaire appelé lorsque le signal show_login_form est émis"""
        from .login import LoginForm  # Import local pour éviter les imports circulaires
        login_form = LoginForm()
        login_form.show_register_form.connect(self.show_register_form_handler)
        login_form.show()
        self.close()

    @classmethod
    def show_register_form_handler(cls, theme=None):
        """Méthode de classe pour créer et afficher le formulaire d'inscription"""
        register_form = cls(theme=theme)
        register_form.show()
        return register_form

    def handle_register(self):
        """Handle registration logic"""
        # Validate all required fields
        required_fields = [
            self.username_field,
            self.email_field,
            self.registration_code_field,
            self.password_field,
            self.confirme_password_field,
            self.secret_question_field,
            self.secret_answer_field
        ]
        
        if not all(field.is_valid() for field in required_fields):
            return
        
        if self.password_field.value != self.confirme_password_field.value:
            self.show_error("Les mots de passe ne correspondent pas")
            return
            
        try:
            # Verify registration code
            reg_controller = RegistrationCodeController()
            code_valid, user_type = reg_controller.verify_code(self.registration_code_field.value)
            
            if not code_valid:
                self.show_error("Code d'inscription invalide ou expiré")
                return
            
            # Create user
            user = self.auth_controller.create_user(
                username=self.username_field.value,
                email=self.email_field.value,
                password=self.password_field.value,
                user_type=user_type,
                secret_question=self.secret_question_field.value,
                secret_answer=self.secret_answer_field.value
            )
            
            if user:
                # Mark registration code as used
                reg_controller.mark_code_as_used(self.registration_code_field.value)
                self.clear_form()
                self.register_success.emit(user)
                # Transition vers le formulaire de connexion après inscription réussie
                self.show_login_form_handler()
            else:
                self.show_error("L'inscription a échoué. Veuillez réessayer.")
                self.register_failed.emit("Registration failed")
                
        except Exception as e:
            self.show_error(str(e))
            self.register_failed.emit(str(e))
    
    def show_error(self, message: str):
        """Display error message"""
        self.error_message.setText(message)
        self.error_message.show()
    
    def clear_form(self):
        """Reset form to initial state"""
        self.username_field.clear_content()
        self.email_field.clear_content()
        self.password_field.clear_content()
        self.confirme_password_field.clear_content()
        self.registration_code_field.clear_content()
        self.secret_answer_field.clear_content()
        self.error_message.hide()
    
    def apply_theme(self):
        """Apply current theme to form"""
        self.setStyleSheet(self.theme.get_stylesheet(form_type=FormType.REGISTER))

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