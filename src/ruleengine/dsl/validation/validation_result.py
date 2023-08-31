from enum import Enum
from dataclasses import dataclass
from typing import Optional

ValidationErrorType = Enum('ValidationErrorType', ['SYNTAX', 'EMPTY', 'NOT_CONDITION', 'NOT_ACTION'])

@dataclass
class ValidationResult:
    success: bool
    error_type: Optional[ValidationErrorType] = None
    error_message: Optional[str] = None

