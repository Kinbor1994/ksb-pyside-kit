"""Card widgets for displaying charts using QtCharts.

This module provides card widgets for displaying pie and bar charts
using the native QtCharts library.
"""

from typing import Optional, Dict, Any
from ...core.commons import (
    Qt,
    QPainter,
    QChart, 
    QChartView,
    QPieSeries,
    QPieSlice,
    QBarSeries,
    QBarSet,
    QBarCategoryAxis,
    QValueAxis,
    QFrame,
    QVBoxLayout,
    QColor,
    QWidget
)
from ...widgets.text import Text
from ..themes.chart_card import ChartTheme, ChartThemes
from ...core.themes.themes import ThemeManager

class ChartBaseCard(QFrame):
    """Base class for chart cards"""
    
    def __init__(
        self,
        title: str,
        description_text: str,
        theme: Optional[ChartTheme] = None,
        parent=None
    ):
        super().__init__(parent)
        self.setObjectName("baseCard")
        self.setFixedHeight(350)
        self.setMinimumWidth(350)
        
        # Properties
        self.title = title
        self.description_text = description_text
        self.theme = theme or ChartThemes.LIGHT
        
        self._cached_data = None  
        
        # Setup UI
        self.setup_ui()
        self.apply_theme()
        
        
    def setup_ui(self):
        """Initialize the card UI components"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(
            self.theme.padding,
            self.theme.padding,
            self.theme.padding,
            self.theme.padding
        )
        self.layout.setSpacing(self.theme.spacing)
        
        # Title
        self.title_label = Text(
            value=self.title,
            theme=ThemeManager.TextThemes.CARD_TITLE_LABEL
        )
        self.layout.addWidget(self.title_label)
        
        # Chart container
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(300)
        self.chart_view.setMinimumWidth(300)
        self.layout.addWidget(self.chart_view)
        
        # Separator
        self.separator = QFrame()
        self.separator.setObjectName("separator")
        self.separator.setFixedHeight(self.theme.separator_height)
        self.separator.setStyleSheet(f"""
            #separator {{
                background-color: {self.theme.separator_color};
                margin: 5px 0px;
            }}
        """)
        self.layout.addWidget(self.separator)
        
        # Footer
        self.footer_label = Text(
            value=self.description_text,
            width=335,
            theme=ThemeManager.TextThemes.CARD_FOOTER_LABEL,
        )
        
        self.layout.addWidget(self.footer_label)
        self.layout.addStretch(1)
        
    def clear_chart(self):
        """Nettoie complètement le graphique"""
        self.chart.removeAllSeries()
        # Supprimer tous les axes
        axes = self.chart.axes()
        for axis in axes:
            self.chart.removeAxis(axis)
            
    def apply_theme(self):
        """Apply current theme to the card"""
        self.setStyleSheet(self.theme.get_card_stylesheet())

class PieChartCard(ChartBaseCard):
    """Card widget for displaying pie charts"""
    
    def __init__(
        self,
        title: str,
        description_text: str,
        data: Dict[str, Any],
        theme: Optional[ChartTheme] = None,
        parent=None
    ):
        super().__init__(title, description_text, theme, parent)
        self.update_chart(data)
        
    def update_chart(self, data: Dict[str, Any]):
        """Update pie chart with new data"""
        self._cached_data = data
        self.clear_chart()
        
        series = QPieSeries()
        for slice_data in data.get("slices", []):
            slice = series.append(slice_data["name"], slice_data["value"])
            color = QColor(slice_data["color"])
            slice.setBrush(color)
            slice.setLabelVisible(True)
            slice.setLabelPosition(QPieSlice.LabelOutside)
            slice.setLabelArmLengthFactor(0.35)
            
        self.chart.addSeries(series)

class BarChartCard(ChartBaseCard):
    """Card widget for displaying bar charts"""
    
    def __init__(
        self,
        title: str,
        description_text: str,
        data: Dict[str, Any],
        theme: Optional[ChartTheme] = None,
        parent=None
    ):
        super().__init__(title, description_text, theme, parent)
        self.update_chart(data)
        
    def update_chart(self, data: Dict[str, Any]):
        """Update bar chart with new data"""
        self._cached_data = data
        self.clear_chart()
        
        series = QBarSeries()
        for serie_data in data.get("series", []):
            bar_set = QBarSet(serie_data["name"])
            color = QColor(serie_data["color"])
            bar_set.setColor(color)
            bar_set.append(serie_data["values"])
            series.append(bar_set)
            
        self.chart.addSeries(series)
        
        # Axe des catégories (X)
        axis_x = QBarCategoryAxis()
        axis_x.append(data.get("categories", []))
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        # Axe des valeurs (Y)
        axis_y = QValueAxis()
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)