from enum import StrEnum
from dataclasses import dataclass, field
from typing import Optional
from ruleengine.dsl.condition import Condition
from ruleengine.dsl.action import Action

ValidationErrorType = StrEnum(
    "ValidationErrorType",
    ["SYNTAX", "EMPTY", "NOT_CONDITION", "NOT_ACTION", "UNDEFINED", "TYPE", "UNKNOWN"],
)


@dataclass
class ValidationResult:
    success: bool

    # If not success, fill in error type and details
    error_type: Optional[ValidationErrorType] = None
    details: dict = field(default_factory=dict)

    # If success, fill in validated entity
    entity: Optional[Action | Condition] = None
