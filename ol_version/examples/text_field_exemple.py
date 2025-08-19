from PySide6.QtWidgets import QApplication, QDialog, QHBoxLayout, QWidget, QVBoxLayout
from PySide6.QtCore import Qt

from ksb_pyside_kit.widgets.text import Text
from ksb_pyside_kit.widgets.text_field import (
    TextField,
    EmailField,
    PasswordField,
    NumberField,
)
from ksb_pyside_kit.widgets.combobox import ComboBox
from ksb_pyside_kit.widgets.date_field import DateField
from ksb_pyside_kit.widgets.button import Button
from ksb_pyside_kit.widgets.textarea import TextArea
from ksb_pyside_kit.widgets.checkbox import Checkbox
from ksb_pyside_kit.widgets.file_field import FileField
from ksb_pyside_kit.core.themes.themes import ThemeManager


class TextFieldDemo(QDialog):
    """Demonstration window for TextField widgets."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TextField Demo")
        self.setStyleSheet("background-color: #f5f5f5;")

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(5)
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        # Add title
        title = Text(
            value="TextField Components Demo",
            theme=ThemeManager.TextThemes.H1_PRIMARY,
            parent=self,
        )
        self.main_layout.addWidget(title)

        self.combobox = ComboBox(
            label="Combobox",
            hint_text="Choisissez une option",
            helper_text="Sélectionnez une option",
            options=[("Option 1", 1), ("Option 2", 2), ("Option 3", 3)],
            parent=self,
        )
        self.main_layout.addWidget(self.combobox)
        
        self.combobox_2 = ComboBox(
            label="Combobox 2",
            hint_text="Choisissez une option",
            theme=ThemeManager.ComboBoxThemes.DARK,
            helper_text="Sélectionnez une option",
            options=[("Option 1", 1), ("Option 2", 2), ("Option 3", 3)],
            parent=self,
        )
        self.main_layout.addWidget(self.combobox_2)

        self.number_field = NumberField(
            label="Age",
            helper_text="Votre âge",
            hint_text="Entrez votre âge",
            min_value=0,
            required=True,
            max_value=20,
            parent=self,
        )
        self.main_layout.addWidget(self.number_field)
        # Standard TextField
        self.text_field = TextField(
            label="Nom",
            hint_text="Entrez votre nom",
            theme=ThemeManager.TextFieldThemes.DARK,
            # helper_text="Le nom doit contenir au moins 2 caractères",
            required=True,
            max_length=50,
            min_length=2,
            parent=self,
        )
        self.main_layout.addWidget(self.text_field)

        phone_field = TextField(
            label="Téléphone",
            hint_text="Ex: +33612345678",
            validation_pattern=r"^\+?(?:[0-9] ?){6,14}[0-9]$",
            validation_message="Numéro de téléphone invalide",
            required=True
        )
        self.main_layout.addWidget(phone_field)
    # Exemple pour sélection multiple
        multiple_file_field = FileField(
            key="multiple_input",
            label="Images à traiter",
            multiple=True,
            file_types=[("Images", ["jpg", "png", "gif"]), ("Tous les fichiers", ["*"])],
            on_change=lambda paths: print(f"{len(paths)} images sélectionnées")
        )
        self.main_layout.addWidget(multiple_file_field)
        
        # Buttons container
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Submit button
        self.submit_button = Button(
            text="Valider",
            theme=ThemeManager.ButtonThemes.PRIMARY,
            on_click=self._handle_submit,
            parent=self,
        )
        buttons_layout.addWidget(self.submit_button)

        # Clear button
        self.clear_button = Button(
            text="Effacer",
            theme=ThemeManager.ButtonThemes.DANGER,
            on_click=self._clear_fields,
            parent=self,
        )
        buttons_layout.addWidget(self.clear_button)

        self.main_layout.addLayout(buttons_layout)
        self.setLayout(self.main_layout)

    def _handle_submit(self):
        """Handle form submission."""
        # Validate all fields
        fields_valid = all(
            [
                self.text_field.is_valid(),
                self.email_field.is_valid(),
                self.password_field.is_valid(),
            ]
        )

        if fields_valid:
            print("Form submitted!")
            print(f"Nom: {self.text_field.get_value()}")
            print(f"Email: {self.email_field.get_value()}")
        else:
            print("Form has errors!")

    def _clear_fields(self):
        """Clear all form fields."""
        self.text_field.clear_content()
        self.email_field.clear_content()


def main():
    """Launch the demo application."""
    import sys

    app = QApplication(sys.argv)

    # Initialize theme system (if needed)
    # initialize_theme_system()

    window = TextFieldDemo()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
