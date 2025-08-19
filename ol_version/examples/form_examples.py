from PySide6.QtWidgets import QDialog, QVBoxLayout, QApplication
import sys

from ksb_pyside_kit.core.themes.themes import ThemeManager
from ksb_pyside_kit.widgets import TextField, EmailField, ComboBox, TextArea, DateField
from ksb_pyside_kit.forms.form import Form, FormModal
from ksb_pyside_kit.forms.base import FieldPosition, FieldAlignment

from ksb_pyside_kit.components.message_box import MessageBox, MessageType, MessageBoxResult
from ksb_pyside_kit.widgets.file_field import FileField
app = QApplication([])


class UserForm(FormModal):

        
    class Meta:
        fields = {
            "username": (
                TextField(
                    label="Nom d'utilisateur",
                    required=True,
                    key="username",
                ),
                FieldPosition(row=0, column=0),  # Première ligne, première colonne
            ),
            "email": (
                EmailField(key="email", label="Email", required=True),
                FieldPosition(row=0, column=1),  # Première ligne, deuxième colonne
            ),
            "date": (
                DateField(key="date", label="Date de naissance", required=True),
                FieldPosition(row=1, column=0),  # Deuxième ligne, première colonne
            ),
            "Description": TextArea(key="description", label="Description", required=True),
            "sexe": ComboBox(key="sexe", label="Sexe", required=True, options=[("Femme", "Femme"), ("Homme", "Homme")]),
            #"file": FileField(label="Fichier", file_types=[("Images",["png", "jpg", "jpeg"])],required=True),
        }
    
    def __init__(self, title = "Form Test", parent = None, show_buttons = True, submit_text = "Test", cancel_text = "Annuler", theme = ThemeManager.FormThemes.DEFAULT):
        super().__init__(title, parent, show_buttons, submit_text, cancel_text, theme)

    def _handle_cancel(self):
        super()._handle_cancel()
        # Afficher une boîte de message de confirmation avant de fermer le formulaire
        response = MessageBox.show_confirm(
            title="Confirmation",
            message="Voulez-vous vraiment annuler ?",
            # yes_text="Oui",
            # no_text="Non",
            parent=self)
        print(str(response))
        if response == MessageBoxResult.YES:
            self.close()
        else:
            print("Annulation annulée.")
    
    def _handle_submit(self):
        super()._handle_submit()
        if self._is_valid():
            
            data = self.get_data()
            print("Submitted data:", data)
            # Vous pouvez ajouter une logique de traitement ici
            # Par exemple, enregistrer les données dans une base de données ou les envoyer à un serveur
            self.close()
            
        else:
            self.show_error("Veuillez corriger les erreurs dans le formulaire.")


from school.controllers import SchoolController
from school.models import SchoolModel
from ksb_pyside_kit.examples.form_model_examples import SchoolFormModel
from ksb_pyside_kit.components.table_view import ModelTableView
class FormDemo(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Form Demo")
        self.setStyleSheet("background-color: #f0f0f0;")
    
        self.main_layout = QVBoxLayout()

        self.form = ModelTableView(
            model_class=SchoolModel,
            controller=SchoolController(),
            title="Schools",
            visible_columns=["name", "address", "city"],
            add_form=SchoolFormModel,
            edit_form=SchoolFormModel,
            theme=ThemeManager.TableThemes.LIGHT,
            parent=self
        )

        self.main_layout.addWidget(self.form)
        self.setLayout(self.main_layout)


if __name__ == "__main__":

    window = UserForm()
    window_2 = FormDemo()
    window_2.setWindowTitle("Form Demo")
    window.show()
    window_2.showMaximized()

    sys.exit(app.exec())
