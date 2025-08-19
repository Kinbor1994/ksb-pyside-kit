from ksb_pyside_kit.settings import UI_CONSTANTS

from ..core.commons import QWidget, QHBoxLayout, QFrame, Signal
from ..widgets.button import IconButton


class NavBar(QFrame):
    """Widget pour la barre de navigation"""

    # Signal pour le toggle du sidebar
    toggle_sidebar = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navbar")
        self.setFixedHeight(UI_CONSTANTS["HEADER_HEIGHT"])

        # Layout principal
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)

        # Bouton toggle sidebar
        self.toggle_button = IconButton(
            icon="fa5s.bars",
            on_click=lambda: self.toggle_sidebar.emit(),
            width=40,
            height=40,
        )
        self.layout.addWidget(self.toggle_button)

        # Espace extensible
        self.layout.addStretch()

        # Zone des actions (à droite)
        self.actions_area = QWidget()
        self.setStyleSheet(
            f"""
            #navbar {{
                min-height: {UI_CONSTANTS["HEADER_HEIGHT"]}px;
                max-height: {UI_CONSTANTS["HEADER_HEIGHT"]}px;
            }}
        """
        )
        self.layout.addWidget(self.actions_area)
