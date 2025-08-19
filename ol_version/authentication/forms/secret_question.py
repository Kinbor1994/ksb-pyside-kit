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
from ...widgets.text_field import TextField
from ...widgets.button import Button
from ...components.image_widget import ImageWidget

from ...widgets.themes.button_themes import ButtonThemes
from ...widgets.themes.text_themes import TextThemes
from ..themes.auth_forms_themes import FormTheme, FormThemes, FormType

class SecretQuestionForm(QDialog):
    """Formulaire de vérification de la question secrète"""
    
    verify_success = Signal(object)  # Émet l'utilisateur vérifié
    verify_failed = Signal(str)
    
    def __init__(self, user: UserModel, theme: Optional[FormTheme] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self._dragging = False
        self._drag_position = QPoint()
        self.setObjectName("secret-question-form")
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
            "ksb_pyside_kit/assets/verification.png",
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
            value="Question secrète",
            theme=TextThemes.H3_PRIMARY
        )
        self.form_layout.addWidget(self.title)
        
        # Question display
        self.question_text = Text(
            value=self.user.secret_question,
            theme=TextThemes.LABEL_INFO_CENTER
        )
        self.form_layout.addWidget(self.question_text)
        
        # Answer field
        self.answer_field = TextField(
            key="answer",
            label="Votre réponse (*)",
            required=True,
            width=340,
            parent=self
        )
        self.form_layout.addWidget(self.answer_field)
        
        # Buttons
        self.button_layout = QHBoxLayout()
        self.verify_button = Button(
            key="verify-btn",
            text="Vérifier",
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
            on_click=self.close
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
        self.apply_theme()
        
    def handle_verify(self):
        """Vérifier la réponse à la question secrète"""
        if not self.answer_field.is_valid():
            return
            
        try:
            if self.auth_controller.verify_secret_answer(
                username=self.user.username,
                answer=self.answer_field.value
            ):
                from .reset_password import ResetPasswordForm
                reset_form = ResetPasswordForm(user=self.user)
                reset_form.show()
                self.close()
            else:
                self.show_error("Réponse incorrecte")
                
        except Exception as e:
            self.show_error(str(e))
            
    def show_error(self, message: str):
        self.error_message.setText(message)
        self.error_message.show()
        
    def apply_theme(self):
        self.setStyleSheet(self.theme.get_stylesheet(form_type=FormType.SECRET_QUESTION))

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
