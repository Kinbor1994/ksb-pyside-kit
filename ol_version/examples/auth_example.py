# Usage example:
from ksb_pyside_kit.authentication.forms.login import LoginForm
from ksb_pyside_kit.authentication.forms.signup import RegisterForm
from ksb_pyside_kit.authentication.forms.forgot_password import ForgotPasswordForm
from ksb_pyside_kit.authentication.forms.reset_password import ResetPasswordForm
from ksb_pyside_kit.authentication.forms.secret_question import SecretQuestionForm
from ksb_pyside_kit.authentication.models.user_model import UserModel
from ksb_pyside_kit.authentication.controllers.user_controller import AuthController
from ksb_pyside_kit.authentication.themes.auth_forms_themes import FormTheme, FormThemes
from ksb_pyside_kit.components.image_widget import ImageWidget
from ksb_pyside_kit.components.themes.image_widget_theme import ImageThemes

from qt_material import apply_stylesheet

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    # Exemple d'utilisation
    
    
    app = QApplication(sys.argv)
    
    def on_auth_success(user):
        print(f"Authentication successful for: {user.username}")
    
    def on_auth_failed(error):
        print(f"Authentication failed: {error}")
    
    def on_forgot_password():
        print("Forgot password clicked")
    
    user = AuthController().get_by_id(1)
    login_form = LoginForm(
        theme=FormThemes.LIGHT,
    )
    
    forgot_password_form = ForgotPasswordForm(theme=FormThemes.LIGHT)   
    reset_password_form = ResetPasswordForm(user=user, theme=FormThemes.LIGHT)
    secret_question_form = SecretQuestionForm(user=user, theme=FormThemes.LIGHT)
    # # Connect signals
    # login_form.auth_success.connect(on_auth_success)
    # login_form.auth_failed.connect(on_auth_failed)
    # login_form.show()
    #forgot_password_form.show()
    #reset_password_form.show()
    secret_question_form.show()
    # signup_form = RegisterForm(theme=FormThemes.LIGHT)
    # signup_form.show()
    sys.exit(app.exec())