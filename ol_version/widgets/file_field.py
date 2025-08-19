from typing import Optional, Any, Callable, Dict, List, Tuple, Union
from pathlib import Path
import os

from PySide6.QtWidgets import QHBoxLayout, QFileDialog
from PySide6.QtCore import Qt

from ..core.commons import QObject, QEvent
from ..core.base_widget import BaseWidget
from ..core.base_form_field import BaseFormField
from ..widgets.text import Text
from ..widgets.button import Button  
from ..widgets.text_field import TextField  
from ..core.themes.themes import ThemeManager

class FileField(BaseFormField):
    """
    A form field widget for file selection with browse button.
    
    Features:
    - Displays selected file path
    - Browse button to open file dialog
    - File type filtering
    - Optional file existence validation
    - Multiple file selection option
    
    Args:
        key (str, optional): Unique identifier for the widget
        width (int, optional): Widget width in pixels
        height (int, optional): Widget height in pixels
        tooltip (str, optional): Hover tooltip text
        visible (bool, optional): Initial visibility state. Defaults to True
        disabled (bool, optional): Initial disabled state. Defaults to False
        theme (Any, optional): Theme configuration to apply
        label (str, optional): Label text displayed above the form field
        hint_text (str, optional): Placeholder text displayed in the widget
        helper_text (str, optional): Helper text displayed below the widget
        error_messages (Dict, optional): Custom error messages for validation
        required (bool, optional): Whether the field is required. Defaults to False
        on_change (Callable, optional): Callback for value change event
        on_focus (Callable, optional): Callback for focus event
        on_blur (Callable, optional): Callback for blur event
        file_types (List[Tuple[str, List[str]]], optional): List of file types as tuples (description, extensions)
        check_exists (bool, optional): Whether to validate that file exists. Defaults to True
        multiple (bool, optional): Whether to allow multiple file selection. Defaults to False
        directory_only (bool, optional): Whether to select directories instead of files. Defaults to False
        button_text (str, optional): Text to display on browse button. Defaults to "Parcourir"
        parent (QWidget, optional): Parent widget. Defaults to None
    """

    def __init__(
        self,
        key: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        tooltip: Optional[str] = None,
        visible: bool = True,
        disabled: bool = False,
        theme: Optional[ThemeManager] = ThemeManager.FileFieldThemes.LIGHT,
        label: Optional[str] = None,
        hint_text: Optional[str] = "Sélectionnez un fichier...",
        helper_text: Optional[str] = None,
        error_messages: Optional[Dict[str, str]] = None,
        required: bool = False,
        on_change: Optional[Callable] = None,
        on_focus: Optional[Callable] = None,
        on_blur: Optional[Callable] = None,
        file_types: Optional[List[Tuple[str, List[str]]]] = None,
        check_exists: bool = True,
        multiple: bool = False,
        directory_only: bool = False,
        button_text: str = "Parcourir",
        parent=None,
    ) -> None:
        """Initialize the file field with file selection functionality."""
        # Store file field specific attributes
        self._file_types = file_types or [("Tous les fichiers", ["*"])]
        self._check_exists = check_exists
        self._multiple = multiple
        self._directory_only = directory_only
        self._button_text = button_text
        self._file_path = None  # Single file path
        self._file_paths = []   # Multiple file paths
        
        # Add custom error messages
        self._custom_error_messages = {
            "file_not_exists": "Le fichier sélectionné n'existe pas",
            "invalid_file_type": "Type de fichier non autorisé",
        }
        
        if error_messages:
            self._custom_error_messages.update(error_messages)
        
        super().__init__(
            key=key,
            width=width,
            height=height,
            tooltip=tooltip,
            visible=visible,
            disabled=disabled,
            theme=theme,
            label=label,
            hint_text=hint_text,
            helper_text=helper_text,
            error_messages=self._custom_error_messages,
            required=required,
            on_change=on_change,
            on_focus=on_focus,
            on_blur=on_blur,
            parent=parent,
        )

    def _create_form_field(self) -> None:
        """Create the file field with text input and browse button."""
        # Create a horizontal layout for the input and button
        field_layout = QHBoxLayout()
        field_layout.setSpacing(2)
        field_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the text input field using your TextField component
        self._input = TextField(
            label="  ",
            hint_text=self._hint_text,
            read_only=True, 
            parent=self, 
        )
        
        # Create the browse button using your Button component
        self._browse_button = Button(
            text=self._button_text,
            width=100,
            height=35,
            on_click=self._show_file_dialog,
            parent=self,
        )
        
        # Set sizes
        if self._width:
            input_width = int(self._width * 0.75)  # 75% for input
            self._input.width = input_width
            button_width = int(self._width * 0.25)  # 25% for button
            self._browse_button.width = button_width
        
        if self._height:
            self._input.height = self._height
            self._browse_button.height = self._height
        
        # Add widgets to the layout
        field_layout.addWidget(self._input)
        field_layout.addWidget(self._browse_button)
        field_layout.addStretch(1) 
        # Add the field layout to the main layout
        self.main_layout.addLayout(field_layout)
        
        # Set the form field widget for event filtering
        self._form_field_widget = self._input
        self._input.installEventFilter(self)

    def _show_file_dialog(self) -> None:
        """Show the file selection dialog based on configuration."""
        file_filter = self._build_file_filter()
        
        if self._directory_only:
            # Open directory selection dialog
            selected_path = QFileDialog.getExistingDirectory(
                self,
                "Sélectionnez un dossier",
                str(Path.home()),
                QFileDialog.ShowDirsOnly
            )
            
            if selected_path:
                self._process_selected_path(selected_path)
        
        elif self._multiple:
            # Open multiple file selection dialog
            selected_files, _ = QFileDialog.getOpenFileNames(
                self,
                "Sélectionnez des fichiers",
                str(Path.home()),
                file_filter
            )
            
            if selected_files:
                self._file_paths = selected_files
                # Display paths with comma separator
                self._input.value = "; ".join(selected_files)
                self.on_value_changed(selected_files)
        
        else:
            # Open single file selection dialog
            selected_file, _ = QFileDialog.getOpenFileName(
                self,
                "Sélectionnez un fichier",
                str(Path.home()),
                file_filter
            )
            
            if selected_file:
                self._process_selected_path(selected_file)

    def _process_selected_path(self, path: str) -> None:
        """Process a selected file or directory path."""
        if path:
            self._file_path = path
            self._file_paths = [path]  # Keep both variables in sync
            self._input.value = path
            self.on_value_changed(path)

    def _build_file_filter(self) -> str:
        """Build file filter string for QFileDialog from file_types configuration."""
        if not self._file_types:
            return "All Files (*)"
        
        filter_parts = []
        for description, extensions in self._file_types:
            extensions_str = " ".join(f"*.{ext.lstrip('*.')}" for ext in extensions)
            filter_parts.append(f"{description} ({extensions_str})")
        
        return ";;".join(filter_parts)

    def get_value(self) -> Union[str, List[str], None]:
        """
        Get the current value of the field (file path or list of paths).
        
        Returns:
            Union[str, List[str], None]: File path, list of file paths, or None
        """
        if self._multiple:
            return self._file_paths
        return self._file_path

    def set_value(self, value: Union[str, List[str], None]) -> bool:
        """
        Set the value of the field.
        
        Args:
            value: File path string, list of file paths, or None
            
        Returns:
            bool: True if value was successfully set, False otherwise
        """
        if value is None:
            self._file_path = None
            self._file_paths = []
            self._input.value = ""
            return True
        
        if self._multiple and isinstance(value, list):
            self._file_paths = value
            self._file_path = value[0] if value else None
            self._input.value = "; ".join(value)
            return True
        
        if isinstance(value, str):
            self._file_path = value
            self._file_paths = [value]
            self._input.value = value
            return True
        
        return False

    def clear_content(self) -> None:
        """Clear the file selection."""
        self._file_path = None
        self._file_paths = []
        self._input.value = ""
        self.reset()

    def is_valid(self) -> bool:
        """
        Validate the field based on file-specific validation rules.
        
        Returns:
            bool: True if valid, False otherwise
        """
        # First run the base validation for required field
        if not super().is_valid():
            return False
        
        value = self.get_value()
        
        # Skip further validation if value is empty and not required
        if not value or (isinstance(value, list) and not value):
            return True
        
        # Check file existence if enabled
        if self._check_exists:
            if self._multiple:
                for path in self._file_paths:
                    if not os.path.exists(path):
                        self.show_error(self._error_messages["file_not_exists"])
                        return False
            elif not os.path.exists(self._file_path):
                self.show_error(self._error_messages["file_not_exists"])
                return False
        
        # Check file type if specified and not directory_only
        if not self._directory_only and self._file_types and self._file_types != [("Tous les fichiers", ["*"])]:
            valid_extensions = []
            for _, extensions in self._file_types:
                for ext in extensions:
                    if ext == "*":
                        return True  # All files allowed
                    valid_extensions.append(ext.lstrip("*.").lower())
            
            # Function to check if a file has valid extension
            def has_valid_extension(filepath):
                _, ext = os.path.splitext(filepath)
                return ext.lstrip(".").lower() in valid_extensions
            
            if self._multiple:
                for path in self._file_paths:
                    if not has_valid_extension(path):
                        self.show_error(self._error_messages["invalid_file_type"])
                        return False
            elif not has_valid_extension(self._file_path):
                self.show_error(self._error_messages["invalid_file_type"])
                return False
        
        self.hide_error()
        return True

    @property
    def file_types(self) -> List[Tuple[str, List[str]]]:
        """Get the allowed file types."""
        return self._file_types
    
    @file_types.setter
    def file_types(self, types: List[Tuple[str, List[str]]]) -> None:
        """Set the allowed file types."""
        self._file_types = types
    
    @property
    def multiple(self) -> bool:
        """Get whether multiple file selection is enabled."""
        return self._multiple
    
    @multiple.setter
    def multiple(self, value: bool) -> None:
        """Set whether multiple file selection is enabled."""
        if self._multiple != value:
            self._multiple = value
            self.clear_content()  # Reset the field when changing mode
    
    @property
    def directory_only(self) -> bool:
        """Get whether directory selection is enabled."""
        return self._directory_only
    
    @directory_only.setter
    def directory_only(self, value: bool) -> None:
        """Set whether directory selection is enabled."""
        if self._directory_only != value:
            self._directory_only = value
            self.clear_content()  # Reset the field when changing mode