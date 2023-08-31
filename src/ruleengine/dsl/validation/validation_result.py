from enum import StrEnum
from dataclasses import dataclass, field
from typing import Optional

ValidationErrorType = StrEnum(
    "ValidationErrorType",
    ["SYNTAX", "EMPTY", "NOT_CONDITION", "NOT_ACTION", "UNDEFINED", "TYPE", "UNKNOWN"],
)


@dataclass
class ValidationResult:
    success: bool
    error_type: Optional[ValidationErrorType] = None
    details: dict = field(default_factory=dict)
