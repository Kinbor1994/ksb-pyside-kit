from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFrame
from PySide6.QtCore import Qt

from ksb_pyside_kit.core.themes.themes import ThemeManager
from ksb_pyside_kit.widgets.text import Text

class TextDemo(QMainWindow):
    """Text widget demonstration window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Démonstration Text Widget")
        self.resize(800, 600)

        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(20)

        # Section 1: Textes simples
        self._add_section(layout, "Styles de texte", [
            Text(
                value="Texte en H1",
                theme=ThemeManager.TextThemes.H1
            ),
            Text(
                value="Texte en H2",
                theme=ThemeManager.TextThemes.H2
            ),
            Text(
                value="Texte en gras",
                theme=ThemeManager.TextThemes.BOLD
            ),
            Text(
                value="Texte en italic",
                theme=ThemeManager.TextThemes.ITALIC
            ),
            Text(
                value="Texte en rouge",
                theme=ThemeManager.TextThemes.DANGER
            ),
            Text(
                value="Texte vert",
                theme=ThemeManager.TextThemes.SUCCESS
            ),
            Text(
                value="helper text",
                icon="fa5s.info-circle",
                icon_color="white",
                theme=ThemeManager.TextThemes.HELPER
            ),
            Text(
                value="Texte d'erreur",
                theme=ThemeManager.TextThemes.ERROR
            ),
            Text(
                value="Texte de title H1 rouge",
                theme=ThemeManager.TextThemes.H1_DANGER
            ),
        ])

        

    def _add_section(self, parent_layout: QVBoxLayout, title: str, widgets: list) -> None:
        """Add a titled section with widgets."""
        # Section frame
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        section_layout = QVBoxLayout(frame)
        
        # Section title
        section_title = Text(
            value=title,
            theme=ThemeManager.TextThemes.H1
        )
        section_layout.addWidget(section_title)
        
        # Add widgets
        for widget in widgets:
            section_layout.addWidget(widget)
            
        parent_layout.addWidget(frame)

def main():
    """Launch the text demo application."""
    import sys
    
    app = QApplication(sys.argv)
    
    window = TextDemo()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()