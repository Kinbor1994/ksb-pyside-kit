from typing import Optional, Dict, Any, List

class ValidationError(Exception):
    """
    Exception raised for form validation errors.
    
    Args:
        message (str): Error message
        field_name (Optional[str]): Name of the field that caused the error
        field_errors (Optional[Dict[str, List[str]]]): Dictionary of field-specific errors
        params (Optional[Dict[str, Any]]): Additional parameters for error formatting
        
    Examples:
        >>> raise ValidationError("Invalid email format")
        >>> raise ValidationError("Required field", field_name="email")
        >>> raise ValidationError("Age must be greater than {min_age}", params={"min_age": 18})
    """
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_errors: Optional[Dict[str, List[str]]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> None:
        self.message = message
        self.field_name = field_name
        self.field_errors = field_errors or {}
        self.params = params or {}
        
        # Format message with params if provided
        if self.params:
            self.message = self.message.format(**self.params)
            
        # Add field-specific error if field_name is provided
        if self.field_name and self.field_name not in self.field_errors:
            self.field_errors[self.field_name] = [self.message]
            
        super().__init__(self.message)

    def add_field_error(self, field_name: str, error: str) -> None:
        """
        Add an error message for a specific field.
        
        Args:
            field_name (str): Name of the field
            error (str): Error message
        """
        if field_name not in self.field_errors:
            self.field_errors[field_name] = []
        self.field_errors[field_name].append(error)

    def get_field_errors(self) -> Dict[str, List[str]]:
        """
        Get all field-specific errors.
        
        Returns:
            Dict[str, List[str]]: Dictionary of field errors
        """
        return self.field_errors

    def __str__(self) -> str:
        """Return formatted error message."""
        if self.field_name:
            return f"{self.field_name}: {self.message}"
        return self.message