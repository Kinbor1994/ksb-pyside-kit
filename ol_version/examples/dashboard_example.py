from PySide6.QtWidgets import QLineEdit, QTableWidget, QStatusBar, QHBoxLayout, QApplication
import sys


from ksb_pyside_kit.components.dashboard import Dashboard, DashboardThemes
from ksb_pyside_kit.components.sidebar import SideBarItem
from ksb_pyside_kit.widgets.text import Text

from ksb_pyside_kit.components.contentarea import Page

from ksb_pyside_kit.components.cards.card import StatCard
from ksb_pyside_kit.components.cards.chart_cards import PieChartCard, BarChartCard

from ksb_pyside_kit.components.themes.chart_card import ChartThemes
from ksb_pyside_kit.core.themes.themes import ThemeManager


class HomePage(Page):
    def __init__(self):
        super().__init__("Accueil")
        
        self.card_layout = QHBoxLayout()
        self.chart_layout = QHBoxLayout()
        self.table_layout = QHBoxLayout()
        
        total_candidate_card = StatCard(
            title="Effectif total",
            value="100",
            description_text="Nombre total des candidats",
            icon="fa6s.children",
            icon_color="#1DC7EA",
        )
        total_female_candidate_card = StatCard(
            title="Effectif total des filles",
            value="60",
            description_text="Nombre total des candidats filles",
            icon="fa6s.child-dress",
            icon_color="#1DC7EA",
        )
        total_male_candidate_card = StatCard(
            title="Effectif total des garçons",
            value="40",
            description_text="Nombre total des candidats garçons",
            icon="fa6s.child",
            icon_color="#1DC7EA",
        )
        self.card_layout.addWidget(total_candidate_card)
        self.card_layout.addWidget(total_female_candidate_card)
        self.card_layout.addWidget(total_male_candidate_card)
        
        # Création des données pour les graphiques
        nb_filles = 60
        nb_garcons = 40
        
        # Données pour le graphique circulaire
        pie_data = {
            "slices": [
                {"name": "Garçons", "value": nb_garcons, "color": "#4169E1"},  # Bleu royal
                {"name": "Filles", "value": nb_filles, "color": "#FF69B1"},  # Rose
            ]
        }
        
        # Données pour le graphique en barres
        bar_data = {
            "categories": ["Répartition par genre"],
            "series": [
                {
                    "name": "Filles",
                    "values": [nb_filles],
                    "color": "#FF69B4"
                },
                {
                    "name": "Garçons",
                    "values": [nb_garcons],
                    "color": "#4169E1"
                }
            ]
        }
        
        # Création des graphiques
        pie_chart = PieChartCard(
            title="Répartition des candidats par genre",
            description_text="Distribution circulaire des effectifs",
            data=pie_data,
            theme=ChartThemes.LIGHT
        )
        
        bar_chart = BarChartCard(
            title="Effectifs par genre",
            description_text="Distribution en barres des effectifs",
            data=bar_data,
            theme=ChartThemes.LIGHT
        )
        
        # Ajout des graphiques
        self.chart_layout.addWidget(pie_chart)
        self.chart_layout.addWidget(bar_chart)
        
        self.layout.addLayout(self.card_layout)
        #self.layout.addLayout(self.chart_layout)
        self.layout.addLayout(self.table_layout)
        
    def on_show(self):
        print("Page d'accueil affichée")


class Page1(Page):
    def __init__(self):
        super().__init__("Page 1")
        self.layout.addWidget(Text("Bienvenue sur la page 1 !"))

    def on_show(self):
        print("Page 1 affichée")


class Page2(Page):
    def __init__(self):
        super().__init__("Page 2")
        self.layout.addWidget(Text("Bienvenue sur la page 2 !"))

    def on_show(self):
        print("Page 2 affichée")


class SettingsPage(Page):
    def __init__(self):
        super().__init__("Paramètres")
        self.layout.addWidget(Text("Page des paramètres"))

    def on_show(self):
        print("Page des paramètres affichée")


class SomePage(Page):
    def __init__(self):
        super().__init__("Some Page")

        self.layout.addWidget(Text("Bienvenue sur some page !"))


class MaPage(Page):
    def __init__(self):
        super().__init__("Ma Page")

    def setup_content(self):
        """Configuration du contenu spécifique de la page"""
        # Création des widgets
        self.search_bar = QLineEdit()
        self.table = QTableWidget()
        self.status_bar = QStatusBar()

        # Ajout des widgets au content_layout
        self.content_layout.addWidget(self.search_bar)
        self.content_layout.addWidget(self.table)
        self.content_layout.addWidget(self.status_bar)

        # Configuration des widgets
        self.search_bar.setPlaceholderText("Rechercher...")
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Status"])

    def load_data(self):
        self.set_loading(True)
        try:
            # Chargement des données...
            pass
        except Exception as e:
            self.show_error(str(e))
        finally:
            self.set_loading(False)


if __name__ == "__main__":
    app = QApplication([])
    
    # Example usage
    menu_items = [
        SideBarItem(
            text="Dashboard",
            icon="fa5s.home",
            tooltip="Home page",
            route="/home",
        ),
        SideBarItem(
            text="Some page",
            icon="fa5s.pager",
            tooltip="User management",
            route="/some",
        ),
        SideBarItem(
            text="Custom Page",
            icon="fa6s.thumbs-up",
            tooltip="Custom page",
            route="/custom",
            on_click=lambda: print("Users clicked"),
        ),
        SideBarItem(
            text="Settings",
            icon="fa6s.gear",
            tooltip="User management",
            route="/settings",
            on_click=lambda: print("Users clicked"),
        ),
    ]

    logo = Text(
        value="MyApp",
        theme=ThemeManager.TextThemes.LOGO,
    )
    colapsed_logo = Text(
        value="MD",
        theme=ThemeManager.TextThemes.LOGO,
    )
    dashboard = Dashboard(
        logo=logo,
        collapsed_logo=colapsed_logo,
        menu_items=menu_items,
        theme=DashboardThemes.LIGHT,
        
    )
    # Ajouter des pages
    dashboard.add_page("/home", HomePage())
    dashboard.add_page("/some", SomePage())
    dashboard.add_page("/settings", SettingsPage())
    dashboard.add_page("/page_2", Page2())
    dashboard.add_page("/custom", MaPage())

    dashboard.showMaximized()
    sys.exit(app.exec())
