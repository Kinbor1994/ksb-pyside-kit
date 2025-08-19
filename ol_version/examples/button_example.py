import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase, QFont

from ksb_pyside_kit.core.themes.themes import ThemeManager
from ksb_pyside_kit.widgets.button import Button, IconButton, TextButton


class ButtonDemo(QMainWindow):
    """Démonstrateur des différents types de boutons."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Démonstration des Boutons")
        self.resize(600, 400)

        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Section Boutons Standards
        standard_frame = self._create_section("Boutons Standards")
        layout.addWidget(standard_frame)
        
        # Section Boutons Icônes
        icon_frame = self._create_section("Boutons avec Icônes")
        layout.addWidget(icon_frame)
        
        # Section Boutons Texte
        text_frame = self._create_section("Boutons Texte")
        layout.addWidget(text_frame)
        
        btn1 = Button(
                text="Bouton Primary",
                theme=ThemeManager.ButtonThemes.PRIMARY,
                on_click=lambda: print("Primary cliqué!"),
                parent=self
            )

        layout.addWidget(btn1)

    def _create_section(self, title: str) -> QFrame:
        """Crée une section de boutons avec un titre."""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        if title == "Boutons Standards":
            # Bouton Primary
            btn1 = Button(
                text="Bouton Primary",
                theme=ThemeManager.ButtonThemes.PRIMARY,
                on_click=lambda: print("Primary cliqué!"),
                parent=self
            )
            layout.addWidget(btn1)
            
            # Bouton Success avec validation
            btn2 = Button(
                text="Bouton Required",
                theme=ThemeManager.ButtonThemes.SUCCESS,
                on_click=lambda: print("Success cliqué!"),
                parent=self
            )
            layout.addWidget(btn2)
            
            # Bouton Danger désactivé
            btn3 = Button(
                text="Bouton Désactivé",
                theme=ThemeManager.ButtonThemes.DANGER,
                disabled=True,
                parent=self
            )
            layout.addWidget(btn3)

        elif title == "Boutons avec Icônes":
            # Bouton avec icône
            btn4 = IconButton(
                icon="fa5s.save",
                tooltip="Sauvegarder",
                theme=ThemeManager.ButtonThemes.PRIMARY,
                on_click=lambda: print("Sauvegarde!"),
                parent=self
            )
            layout.addWidget(btn4)
            
            # Bouton avec icône et texte
            btn5 = Button(
                text="Supprimer",
                icon="fa5s.trash",
                icon_color="white",
                theme=ThemeManager.ButtonThemes.DANGER,
                on_click=lambda: print("Suppression!"),
                parent=self
            )
            layout.addWidget(btn5)

        else:  # Boutons Texte
            # Bouton texte standard
            btn6 = TextButton(
                text="Lien Simple",
                theme=ThemeManager.ButtonThemes.PRIMARY,
                on_click=lambda: print("Lien cliqué!"),
                parent=self
            )
            layout.addWidget(btn6)
            
            # Bouton texte avec erreur
            btn7 = TextButton(
                text="Lien avec Erreur",
                theme=ThemeManager.ButtonThemes.DANGER,
                parent=self,
            )
            layout.addWidget(btn7)

        return frame

def main():
    app = QApplication(sys.argv)
    
    # # Initialisation du système de thèmes
    # ThemeManager.initialize(show_warnings=True) 
    
    
    window = ButtonDemo()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()