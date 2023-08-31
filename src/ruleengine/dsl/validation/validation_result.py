from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

ValidationErrorType = Enum(
    "ValidationErrorType",
    ["SYNTAX", "EMPTY", "NOT_CONDITION", "NOT_ACTION", "UNDEFINED"],
)


@dataclass
class ValidationResult:
    success: bool
    error_type: Optional[ValidationErrorType] = None
    details: dict = field(default_factory=dict)
