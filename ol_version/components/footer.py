from ksb_pyside_kit.settings import UI_CONSTANTS, APP_NAME, APP_VERSION
from ..core.commons import QHBoxLayout, QFrame
from ..widgets.text import Text
from ..core.themes.themes import ThemeManager

class Footer(QFrame):
    """Widget pour le pied de page"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("footer")
        self.setFixedHeight(UI_CONSTANTS["FOOTER_HEIGHT"])

        # Layout principal
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)

        # Copyright avec le nouveau système de thèmes
        self.copyright = Text(
            value=f"© 2025 {APP_NAME}. Tous droits réservés. Version {APP_VERSION}",
            width=600,
            theme=ThemeManager.TextThemes.LABEL,
        )
        self.layout.addWidget(self.copyright)
        
        self.setStyleSheet(f"""
            #footer {{
                min-height: {UI_CONSTANTS["FOOTER_HEIGHT"]}px;
                max-height: {UI_CONSTANTS["FOOTER_HEIGHT"]}px;
            }}
        """)

        # Espace extensible
        self.layout.addStretch()
