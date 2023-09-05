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
    entity: Optional[Action | Condition] = None
    error_type: Optional[ValidationErrorType] = None
    details: dict = field(default_factory=dict)
