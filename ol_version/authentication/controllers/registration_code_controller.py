from datetime import datetime
from typing import Tuple, Optional
from ..models.registration_code_model import RegistrationCodeModel
from ..models.user_model import UserType
from ...controllers.base_controller import BaseController

class RegistrationCodeController(BaseController):
    def __init__(self):
        super().__init__(RegistrationCodeModel)
    
    def verify_code(self, code: str) -> Tuple[bool, Optional[UserType]]:
        """
        Verify if registration code is valid and not expired
        Returns (is_valid, user_type)
        """
        try:
            codes = self.find_by_attributes(code=code, is_used=False)
            if not codes:
                return False, None
                
            reg_code = codes[0]
            
            # Check if code is expired
            if reg_code.expiration_date < datetime.now():
                return False, None
                
            return True, reg_code.user_type
            
        except Exception:
            return False, None
    
    def mark_code_as_used(self, code: str) -> bool:
        """Mark registration code as used"""
        try:
            codes = self.find_by_attributes(code=code)
            if not codes:
                return False
                
            reg_code = codes[0]
            return self.update(reg_code.id, is_used=True)
            
        except Exception:
            return False
