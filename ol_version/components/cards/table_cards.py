"""Card widget for displaying tables.

This module provides a card widget for displaying data in a table format,
with a simplified version of GenericTableView.
"""

from typing import Optional, List, Dict, Any
from ...core.commons import (
    QFrame,
    QVBoxLayout,
    QTableView,
    QHeaderView,
    Qt,
    QAbstractTableModel,
    QModelIndex,
    QColor,
)
from ...widgets.text import Text
from ..themes.table_card import TableCardTheme, TableCardThemes
from ...core.themes.themes import ThemeManager

class TableCardModel(QAbstractTableModel):
    """Simple table model for TableCard"""
    
    def __init__(self, headers: List[str], data: List[Dict[str, Any]], parent=None):
        super().__init__(parent)
        self.headers = headers
        self._data = data
        
    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._data)
        
    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.headers)
        
    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None
            
        if role == Qt.DisplayRole:
            return str(self._data[index.row()].get(self.headers[index.column()], ""))
            
        elif role == Qt.TextAlignmentRole:
            value = self._data[index.row()].get(self.headers[index.column()])
            if isinstance(value, (int, float)):
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter
            
        return None
        
    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None

    def update_data(self, new_data: List[Dict[str, Any]]):
        """Update model data"""
        self._data = new_data
        self.layoutChanged.emit()
        
class TableCard(QFrame):
    """Card widget for displaying tables
    
    A lightweight table display with card styling, useful for showing
    summarized or limited data sets.
    """
    
    def __init__(
        self,
        title: str,
        description: str,
        headers: List[str],
        data: List[Dict[str, Any]],
        theme: Optional[TableCardTheme] = None,  
        max_rows: int = 5,
        parent=None
    ):
        super().__init__(parent)
        self.setObjectName("baseCard")
        self.title = title
        self.description = description
        self.headers = headers
        self.data = data[:max_rows]
        self.theme = theme or TableCardThemes.LIGHT  
        self.max_rows = max_rows
        
        self.setup_ui()
        self.apply_theme()
        
    def setup_ui(self):
        """Initialize the card UI components"""
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
        
        # Table
        self.table = QTableView()
        self.table.setWordWrap(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        
        # Set model
        self.model = TableCardModel(self.headers, self.data)
        self.table.setModel(self.model)
        self.table.setMinimumHeight(300)
        self.table.setMinimumWidth(300)
        self.layout.addWidget(self.table)
        
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
        
        # Footer with description
        self.footer_label = Text(
            value=self.description,
            width=335,
            theme=ThemeManager.TextThemes.CARD_FOOTER_LABEL,
        )
        
        self.layout.addWidget(self.footer_label)
        self.layout.addStretch(1)
        
    def apply_theme(self):
        """Apply theme to the card and table"""
        self.setStyleSheet(self.theme.get_card_stylesheet())
        self.table.setStyleSheet(self.theme.get_table_stylesheet())
        
    def update_data(self, new_data: List[Dict[str, Any]]):
        """Update table with new data
        
        Args:
            new_data: New data to display in table
        """
        self.data = new_data[:self.max_rows]
        self.model.update_data(self.data) 