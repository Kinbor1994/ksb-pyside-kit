from dataclasses import dataclass
from typing import Type, List, Any, Optional, Dict

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column
from PySide6.QtCore import Signal

from ..core.commons import (
    QTableView,
    Qt,
    QDialog,
    QAbstractTableModel,
    QModelIndex,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QHeaderView,
    QMessageBox,
    QMenu,
)
from ..forms.form import Form
from ..widgets.button import Button
from ..core.themes.themes import ThemeManager, TableTheme
from ..widgets.text_field import TextField
from ..widgets.combobox import ComboBox
from ..widgets.separator import Separator
from ..widgets.text import Text

from ..models.metadata import ColumnMetadata
from ..forms.model_form import FormModelModal, FormMode
from ..components.message_box import MessageBox, MessageBoxResult

class TableModel(QAbstractTableModel):
    """Generic model for handling tabular data from SQLAlchemy models"""

    def __init__(self, headers: List[str], columns: List[str], parent=None):
        super().__init__(parent)
        self._original_data = []
        self._data = []
        self._headers = headers
        self._columns = columns  

    def update_data(self, new_data: List[Any]):
        """Update the model with new data"""
        self.layoutAboutToBeChanged.emit()
        self._original_data = new_data
        self._data = new_data.copy()
        self.layoutChanged.emit()
        
    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            item = self._data[index.row()]
            column_name = self._columns[index.column()]
            
            if "_id" in column_name:
                relation_name = column_name.replace("_id", "")
                if hasattr(item, relation_name):
                    related_item = getattr(item, relation_name)
                    column = item.__table__.columns.get(column_name)
                    if isinstance(column.info, ColumnMetadata) and column.info.related_info:
                        related_column = column.info.related_info.get("related_column")
                        if related_column and hasattr(related_item, related_column):
                            return str(getattr(related_item, related_column))
                    return str(related_item)
            
            value = getattr(item, column_name, "")
            
            if isinstance(value, bool):
                return "Oui" if value else "Non"
            elif isinstance(value, (int, float)):
                return f"{value:,}".replace(",", " ") 
            elif hasattr(value, "strftime"):  
                return value.strftime("%d/%m/%Y")
            elif hasattr(value, "__table__"): 
                return str(getattr(value, "name", str(value)))
            
            return str(value) if value is not None else ""

        elif role == Qt.TextAlignmentRole:
            item = self._data[index.row()]
            column_name = self._columns[index.column()]
            value = getattr(item, column_name, "")
            
            if isinstance(value, (int, float)):
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        return None

    def filter_data(self, filters: Dict[str, str]):
        """
        Filter data based on column filters
        
        Args:
            filters: Dictionary of column names and filter values
        """
        self.layoutAboutToBeChanged.emit()
        
        # Reset to original data
        self._data = self._original_data.copy()
        
        # Apply each filter
        for column, value in filters.items():
            if not value:  # Skip empty filters
                continue
                
            filtered_data = []
            for item in self._data:
                item_value = getattr(item, column, None)
                
                # SQLAlchemy relationship handling
                if hasattr(item_value, '__table__'):
                    item_value = str(item_value)
                # Boolean handling
                elif isinstance(item_value, bool):
                    item_value = "Oui" if item_value else "Non"
                # Date handling
                elif hasattr(item_value, 'strftime'):
                    item_value = item_value.strftime("%d/%m/%Y")
                else:
                    item_value = str(item_value) if item_value is not None else ""

                if str(value).lower() in str(item_value).lower():
                    filtered_data.append(item)
                    
            self._data = filtered_data
            
        self.layoutChanged.emit()
        
    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(section + 1)
        return None

class TableView(QWidget):
    """
    Generic table view for manual data handling.
    
    Provides a configurable table interface where columns and data 
    can be manually defined.
    """
    record_added = Signal(object)  # Émis quand un enregistrement est ajouté
    record_updated = Signal(object)  # Émis quand un enregistrement est modifié
    record_deleted = Signal(int)  # Émis quand un enregistrement est supprimé
    
    def __init__(
        self,
        columns: List[Dict[str, Any]],
        title: str,
        add_form=None,
        edit_form=None,
        visible_columns: Optional[List[str]] = None,
        theme: Optional[TableTheme] = ThemeManager.TableThemes.DARK,
        parent=None,
    ):
        """
        Initialize TableView.

        Args:
            columns: List of column definitions
            title: Table title
            add_form: Form class for adding records
            edit_form: Form class for editing records
            theme: Table theme configuration
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.title = title
        self.columns = columns
        self.add_form = add_form
        self.edit_form = edit_form
        self.visible_columns = visible_columns or [col["key"] for col in columns]
        
        self._theme = theme
        self._setup_ui()
        self._setup_table() 
        self.apply_theme(self._theme)
        
    def _setup_ui(self):
        """Initialize the UI components"""
        self._main_layout = QVBoxLayout()
        self._main_layout.setContentsMargins(5, 5, 5, 5)
        self._main_layout.setSpacing(5)

        # Header Section
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.title_label = Text(value=self.title, theme=ThemeManager.TextThemes.H4)
        self.header_layout.addWidget(self.title_label)
        
        self.header_layout.addStretch(1)
        if self.add_form:
            self.add_button = Button(
                text="Nouveau",
                icon="fa5s.plus",
                theme=ThemeManager.ButtonThemes.PRIMARY, 
                on_click=self.on_add_clicked,
                parent=self,
            )
            self.header_layout.addWidget(self.add_button)
        
        
        self._main_layout.addLayout(self.header_layout)
        
        separator = Separator(orientation="horizontal")
        self._main_layout.addWidget(separator)
        
        # Add specific filter fields layout
        self.specific_fields_layout = QVBoxLayout()
        self.specific_fields_layout.setContentsMargins(0, 0, 0, 0)
        self.specific_fields_layout.setSpacing(2)
        self._main_layout.addLayout(self.specific_fields_layout)
        
        # Add specific widgets layout
        self.specific_widgets_layout = QHBoxLayout()
        self.specific_widgets_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.addLayout(self.specific_widgets_layout)
        
        # Table view
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.resizeColumnsToContents()
        self.table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_context_menu)
        self.table_view.doubleClicked.connect(self.on_row_double_clicked)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._main_layout.addWidget(self.table_view, 1)

        self.setLayout(self._main_layout)
        
        
    def _setup_table(self):
        """Setup table model and initial data"""
        visible_columns_data = [col for col in self.columns if col["key"] in self.visible_columns]
        self.table_model = TableModel(
            headers=[col["label"] for col in visible_columns_data],
            columns=[col["key"] for col in visible_columns_data]
        )
        self.table_view.setModel(self.table_model)
        self.table_view.setStyleSheet(self._theme.get_stylesheet())
        self.table_view.resizeColumnsToContents()

    def set_theme(self, theme: TableTheme):
        """
        Load a new theme.
        
        Args:
            theme (TableTheme): Theme to apply.
        """
        self._theme = theme
        self._setup_table()
            
    def add_specific_field_widget(self, widget: QWidget):
        """Add a specific field widget to the layout"""
        self.specific_fields_layout.addWidget(widget)
        
    def add_specific_widget(self, widget: QWidget):
        """Add a specific widget to the layout"""
        self.specific_widgets_layout.addWidget(widget)
        # Remove any existing stretch to ensure proper layout
        for i in range(self.specific_widgets_layout.count()):
            item = self.specific_widgets_layout.itemAt(i)
            if item and item.spacerItem():
                self.specific_widgets_layout.removeItem(item)
        # Add a stretch at the end to push widgets to the left
        self.specific_widgets_layout.addStretch(1)
    
    def show_context_menu(self, position):
        """Show context menu for row operations"""
        index = self.table_view.indexAt(position)
        if not index.isValid():
            return

        menu = QMenu(self)
        
        if self.edit_form:
            edit_action = menu.addAction("Modifier")
            edit_action.triggered.connect(lambda: self.on_edit_clicked(index.row()))

        delete_action = menu.addAction("Supprimer")
        delete_action.triggered.connect(lambda: self.on_delete_clicked(index.row()))

        menu.exec_(self.table_view.viewport().mapToGlobal(position))
        

    def on_add_clicked(self):
        """Handle add new record"""
        if not self.add_form:
            return
            
        dialog = self.add_form()
        dialog.submitted.connect(self._handle_record_added)
        dialog.exec()

    def on_edit_clicked(self, row: int):
        """Handle edit record"""
        if not self.edit_form:
            return
            
        try:
            item = self.table_model._data[row]
            dialog = self.edit_form(instance=item)
            dialog.submitted.connect(self._handle_record_updated)
            dialog.exec()
                
        except Exception as e:
            MessageBox.show_error(
                title="Erreur",
                message=f"Erreur lors de la modification:\n{str(e)}",
                parent=self
                )

    def on_delete_clicked(self, row: int):
        """Handle delete record"""
        try:
            item = self.table_model._data[row]

            reply = MessageBox.show_confirm(
                title="Confirmation de suppression",
                message="Voulez-vous vraiment supprimer cet enregistrement ?",
                parent=self
            )
            
            if reply == MessageBoxResult.YES:
                self.controller.delete(item.id)
                # Recharger avec les filtres actuels
                self._handle_record_deleted(item.id)
                
        except Exception as e:
            MessageBox.show_error(
                title="Erreur",
                message=f"Erreur lors de la suppression:\n{str(e)}",
                parent=self
            )

    def refresh_data(self):
        """Reload data from the controller"""
        pass
    
    def on_filter_changed(self, key: str, value: Any):
        """Handle filter change"""
        pass
    
    def _apply_filters(self):
        """Apply filters to the table model"""
        pass
    
    def on_row_double_clicked(self, index: QModelIndex):
        """Handle row double click - opens edit form"""
        self.on_edit_clicked(index.row())

    def apply_theme(self, theme: ThemeManager) -> None:
        """
        Apply a theme to the widget.
        
        Args:
            theme: Theme configuration to apply
        """
        if theme and hasattr(theme, 'get_stylesheet'):
            self.setStyleSheet(theme.get_stylesheet())
            self._theme = theme
        
    def _handle_record_added(self, data: dict):
        """Handle new record added"""
        self.record_added.emit(data)
        self._apply_filters()  
        

    def _handle_record_updated(self, data: dict):
        """Handle record updated"""
        self.record_updated.emit(data)
        self._apply_filters()  
        

    def _handle_record_deleted(self, id_: int):
        """Handle record deleted"""
        self.record_deleted.emit(id_)
        self._apply_filters()
        
class ModelTableView(TableView):
    """
    Table view generated from SQLAlchemy model.
    
    Automatically generates table structure and forms from model metadata.
    """

    def __init__(
        self,
        model_class: Type[DeclarativeBase],
        controller: Any,
        title: str,
        visible_columns: Optional[List[str]] = None,
        add_form: Optional[Type[FormModelModal]] = None,
        edit_form: Optional[Type[FormModelModal]] = None,
        theme: Optional[TableTheme] = ThemeManager.TableThemes.LIGHT,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize ModelTableView.

        Args:
            model_class: SQLAlchemy model class
            controller: Data controller instance
            title: Table title
            visible_columns: List of visible columns (optional)
            add_form: Custom form for adding records (optional)
            edit_form: Custom form for editing records (optional)
            theme: Table theme configuration
            parent: Parent widget
        """
        self.model_class = model_class
        self.controller = controller
        
        # Generate columns from model
        columns = self._generate_columns_from_model()
        visible_columns = visible_columns or columns
        super().__init__(
            columns=columns,
            title=title,
            add_form=add_form,
            edit_form=edit_form or self._get_default_edit_form(),
            visible_columns=visible_columns,
            theme=theme,
            parent=parent
        )
        self._setup_filters()
        self._filters = {} 
        
        self.record_added.connect(self._on_record_changed)
        self.record_updated.connect(self._on_record_changed)
        self.record_deleted.connect(self._on_record_deleted)
        
    def _generate_columns_from_model(self) -> List[Dict[str, Any]]:
        """Generate column definitions from model metadata"""
        columns = []
        
        for column in self.model_class.__table__.columns:
            if not isinstance(column.info, ColumnMetadata):
                continue
                
            metadata = column.info
            if not metadata.common_attributes.get("visible", True):
                continue
                
            columns.append({
                "key": column.key,
                "label": metadata.common_attributes.get("label", column.name),
                "sortable": metadata.sortable,
                "filterable": metadata.filterable,
                "type": column.type.__class__.__name__.lower()
            })
            
        return columns

    
    def _create_filter_field(self, column: Column, metadata: ColumnMetadata) -> Optional[QWidget]:
        """Create appropriate filter field based on metadata"""
        field_type = metadata.filter_type
        if not field_type:
            return None
        
        key = metadata.common_attributes["key"]
        
        if column.foreign_keys:
            field = ComboBox(
                key=key,
                label=metadata.common_attributes["label"],
                required=False
            )
            try:
                related_items = self.controller.get_related_model_items(column.name)
                if related_items:
                    options = [(str(item), item.id) for item in related_items]
                    field.set_options(options)
                    
            except Exception as e:
                MessageBox.show_error(
                    title="Erreur",
                    message=f"Erreur lors de la récupération des options:\n{str(e)}",
                    parent=self
                )
                
            return field
        
        elif field_type == ComboBox:
            field = ComboBox(
                key=key,
                label=metadata.common_attributes["label"],
                required=False
            )
        
            options = metadata.field_attributes.get("options", [])
            field.set_options(options)
            return field
        
        # Default to generic field
        return field_type(
            key=key,
            label=metadata.common_attributes["label"],
            required=False
        )
        
    def _get_default_add_form(self) -> Type[FormModelModal]:
        """Create default add form if none provided"""
        return lambda: FormModelModal(
            model_class=self.model_class,
            controller=self.controller,
            mode=FormMode.CREATE,
            title=f"Nouveau {self.model_class.__verbose_name__}"
        )

    def _get_default_edit_form(self) -> Type[FormModelModal]:
        """Create default edit form if none provided"""
        return lambda instance: FormModelModal(
            model_class=self.model_class,
            controller=self.controller,
            instance=instance,
            mode=FormMode.UPDATE,
            title=f"Modifier {instance}"
        )

    def refresh_data(self):
        """Reload data from controller"""
        try:
            data = self.controller.get_all()
            self.table_model.update_data(data)
        except Exception as e:
            MessageBox.show_error(
                title="Erreur",
                message=f"Erreur lors de la récupération des données:\n{str(e)}",
                parent=self
            )
            
    def _setup_filters(self):
        """Setup filter fields based on model metadata"""
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        has_filters = False
        self._filter_fields = {}  
        
        for column in self.model_class.__table__.columns:
            if not isinstance(column.info, ColumnMetadata):
                continue
                
            metadata = column.info
            if not metadata.filterable:
                continue
                
            has_filters = True
            
            filter_field = self._create_filter_field(column,metadata)
            if filter_field:
                filter_widget = QWidget()
                filter_widget_layout = QVBoxLayout(filter_widget)
                filter_widget_layout.setContentsMargins(0, 0, 0, 0)
                
                filter_widget_layout.addWidget(filter_field)
                
                filter_layout.addWidget(filter_widget)
                
                self._filter_fields[metadata.common_attributes["key"]] = filter_field
                
                if isinstance(filter_field, TextField):
                    filter_field._on_change = lambda value, key=metadata.common_attributes["key"]: self._on_filter_changed(key, value)
            
                elif isinstance(filter_field, ComboBox):
                    filter_field._on_change = lambda value, key=metadata.common_attributes["key"]: self._on_filter_changed(key, value)

        if has_filters:
            search_button = Button(
                text="Rechercher",
                icon="fa5s.search",
                theme=ThemeManager.ButtonThemes.PRIMARY,
                on_click=self._apply_filters
            )
            self.add_specific_widget(search_button)
            
            reset_button = Button(
                text="Réinitialiser",
                icon="fa5s.undo",
                theme=ThemeManager.ButtonThemes.SECONDARY,
                on_click=self._reset_filters
            )
            self.add_specific_widget(reset_button)
            
            filter_layout.addStretch(1)
            
            self.specific_fields_layout.addLayout(filter_layout)

    def _on_filter_changed(self, key: str, value: Any):
        """Handle filter value changes"""
        self._filters[key] = value
        self._apply_filters()  

    def _on_record_changed(self, data: dict):
        """Handle record added or updated"""
        self._apply_filters()  # Recharger les données avec les filtres actuels

    def _on_record_deleted(self, id_: int):
        """Handle record deleted"""
        self._apply_filters()  # Recharger les données avec les filtres actuels

    def _apply_filters(self):
        """Apply current filters and load data"""
        try:
            # Récupérer les valeurs actuelles des champs de filtre
            criteria = {}
            for key, field in self._filter_fields.items():
                value = field.get_value()
                if value:
                    if "." in key:
                        # Pour les foreign keys, utiliser l'ID
                        base_key = key.split(".")[0]
                        criteria[f"{base_key}_id"] = value
                    else:
                        criteria[key] = value
            
            # Obtenir les colonnes de tri
            sort_columns = []
            for column in self.model_class.__table__.columns:
                if (isinstance(column.info, ColumnMetadata) and 
                    column.info.sortable):
                    sort_columns.append(column.key)
            
            # Récupérer les données avec filtres et tri
            data = self.controller.get_filtered(
                filters=criteria,
                sort_by=sort_columns
            )
            
            # Mettre à jour le tableau
            self.table_model.update_data(data)
            
        except Exception as e:
            MessageBox.show_error(
                title="Erreur",
                message=f"Erreur lors du chargement des données:\n{str(e)}",
                parent=self
            )

    def _reset_filters(self):
        """Reset all filters to default values"""
        self._filters.clear()
        
        # Réinitialiser les champs de filtre
        for field in self._filter_fields.values():
            if hasattr(field, 'clear_content'):
                field.clear_content()
        
        # Recharger les données sans filtre
        self._apply_filters()
        
        