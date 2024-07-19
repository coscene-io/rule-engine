# Copyright 2024 coScene
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from ruleengine.dsl.action import Action
from ruleengine.dsl.condition import Condition

ValidationErrorType = Enum(
    "ValidationErrorType",
    ["SYNTAX", "EMPTY", "NOT_CONDITION", "NOT_ACTION", "UNDEFINED", "UNKNOWN"],
)


@dataclass
class ValidationResult:
    success: bool

    # If not success, fill in error type and details
    error_type: Optional[ValidationErrorType] = None
    details: dict = field(default_factory=dict)

    # If success, fill in validated entity
    entity: Optional[Action or Condition] = None

    def __post_init__(self):
        if self.success:
            assert self.entity is not None
        else:
            assert self.error_type
