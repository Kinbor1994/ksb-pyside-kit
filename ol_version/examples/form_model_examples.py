from PySide6.QtWidgets import QDialog, QVBoxLayout
from ksb_pyside_kit.core.themes.themes import ThemeManager
from ksb_pyside_kit.forms.model_form import FormModel, FormModelModal, FormMode
from school.models import SchoolModel
from ksb_pyside_kit.controllers.base_controller import BaseController

from school.controllers import SchoolController

class SchoolFormModel(FormModelModal):
    
    def __init__(self, model_class=SchoolModel, instance=None, mode=FormMode.CREATE, controller=SchoolController(), title = "CEG", parent = None):
        super().__init__(model_class=model_class, instance=instance, mode=mode, controller=controller, title=title, parent=parent)
        
# Pour créer un nouveau


# # Pour éditer un existant
# school_to_edit = school_controller.get_by_id(1)
# edit_school_form = FormModel(
#     model_class=SchoolModel,
#     controller=school_controller,
#     instance=school_to_edit
# )
# edit_school_form.show()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    
    new_school_form = SchoolFormModel()
    new_school_form.show()

    sys.exit(app.exec())