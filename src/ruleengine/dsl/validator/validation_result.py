from enum import Enum
from dataclasses import dataclass

ErrorType = Enum('ErrorType', ['SYNTAX'])

@dataclass
class ValidationResult:
    success: bool
    error_type: ErrorType
    error_details: dict

