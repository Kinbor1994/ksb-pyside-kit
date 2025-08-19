from datetime import datetime
from typing import Optional, Tuple
import bcrypt
import re
from ..models.user_model import UserModel, UserType
from ...controllers.base_controller import BaseController

class PasswordValidationError(Exception):
    """Exception raised when password validation fails"""
    pass

class AuthController(BaseController):
    # Password validation constants
    MIN_LENGTH = 8
    MAX_LENGTH = 50
    
    def __init__(self):
        super().__init__(UserModel)

    def _validate_password(self, password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password against security criteria.
        
        Args:
            password (str): Password to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
            
        Criteria:
        - Length between MIN_LENGTH and MAX_LENGTH characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        # Check length
        if not self.MIN_LENGTH <= len(password) <= self.MAX_LENGTH:
            return False, f"Password must be between {self.MIN_LENGTH} and {self.MAX_LENGTH} characters"

        # Check for uppercase
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"

        # Check for lowercase
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"

        # Check for digits
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"

        # Check for special characters
        if not re.search(r'[ !@#$%&\'()*+,-./[\\\]^_`{|}~"]', password):
            return False, "Password must contain at least one special character"

        return True, None

    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        # Convert the password to bytes
        password_bytes = password.encode('utf-8')
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        # Return the hashed password as string
        return hashed.decode('utf-8')

    def _check_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        # Convert strings to bytes
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        # Check the password
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        secret_question: str,
        secret_answer: str,
        first_name: str = None,
        last_name: str = None,
        user_type: UserType = UserType.DEFAULT,
    ) -> Optional[UserModel]:
        """
        Create a new user with password validation.
        
        Args:
            username (str): Username
            email (str): Email address
            password (str): Password (will be validated and hashed)
            secret_question (str): Security question
            secret_answer (str): Answer to security question
            first_name (str, optional): User's first name
            last_name (str, optional): User's last name
            user_type (UserType, optional): User type/role
            
        Returns:
            Optional[UserModel]: Created user or None if creation fails
            
        Raises:
            PasswordValidationError: If password doesn't meet security criteria
        """
        try:
            # Validate password
            is_valid, error_message = self._validate_password(password)
            if not is_valid:
                raise PasswordValidationError(error_message)

            # Check if username or email exists
            if self.exists(username=username) or self.exists(email=email):
                return None

            # Hash password and secret answer
            hashed_password = self._hash_password(password)
            hashed_answer = self._hash_password(secret_answer.lower())

            # Create user
            return self.create(
                username=username,
                email=email,
                password=hashed_password,
                secret_question=secret_question,
                secret_answer=hashed_answer,
                first_name=first_name,
                last_name=last_name,
                user_type=user_type,
                date_joined=datetime.now(),
            )
        except PasswordValidationError:
            raise
        except Exception:
            return None

    def change_password(self, user_id: int, new_password: str) -> bool:
        """
        Change user's password with validation.
        
        Args:
            user_id (int): User ID
            new_password (str): New password to set
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            PasswordValidationError: If new password doesn't meet security criteria
        """
        try:
            # Validate new password
            is_valid, error_message = self._validate_password(new_password)
            if not is_valid:
                raise PasswordValidationError(error_message)

            # Hash and update password
            hashed_password = self._hash_password(new_password)
            self.update(user_id, password=hashed_password)
            return True
        except PasswordValidationError:
            raise
        except Exception:
            return False
        
    def verify_secret_answer(self, username: str, answer: str) -> bool:
        """Verify user's secret answer"""
        try:
            user = self.find_by_attributes(username=username)
            if not user:
                return False

            user = user[0]
            return self._check_password(answer.lower(), user.secret_answer)
        except Exception:
            return False

    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        try:
            self.update(user_id, last_login=datetime.now())
            return True
        except Exception:
            return False

    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[UserModel]]:
        """
        Authenticate a user with username and password.
        
        Args:
            username (str): The username to authenticate
            password (str): The password to verify
            
        Returns:
            Tuple[bool, Optional[UserModel]]: A tuple containing:
                - bool: True if authentication successful, False otherwise
                - Optional[UserModel]: The authenticated user or None if authentication failed
        """
        try:
            # Find user by username
            user = self.find_by_attributes(username=username)
            if not user:
                return False, None
                
            user = user[0]  # Get first user since username is unique
            
            # Check if user is active
            if not user.is_active:
                return False, None
                
            # Verify password
            if self._check_password(password, user.password):
                # Update last login timestamp
                self.update_last_login(user.id)
                return True, user
                
            return False, None
            
        except Exception as e:
            return False, None
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        try:
            user = self.get_by_id(user_id)
            return user.user_type == UserType.ADMIN
        except Exception:
            return False

    def is_manager(self, user_id: int) -> bool:
        """Check if user is manager"""
        try:
            user = self.get_by_id(user_id)
            return user.user_type == UserType.MANAGER
        except Exception:
            return False