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
import logging
from enum import IntEnum
from functools import wraps
from typing import Optional

import celpy
from pydantic import BaseModel

# Define the CEL environment
ENV = celpy.Environment(
    annotations={
        "msg": celpy.celtypes.MapType,
        "scope": celpy.celtypes.MapType,
        "topic": celpy.celtypes.StringType,
        "ts": celpy.celtypes.DoubleType,
    }
)


# Define the enums/constants related to validation errors
class ErrorSectionEnum(IntEnum):
    """Define the enumeration for the error section"""

    CONDITION = 1
    ACTION = 2


class ValidationErrorLocation(BaseModel):
    """Define the structure of the validation error location"""

    ruleIndex: int
    section: ErrorSectionEnum
    itemIndex: Optional[int] = None


class ValidationErrorUnexpectedVersion(BaseModel):
    """Define the structure of the validation error unexpected version"""

    allowedVersions: list[str]


class ValidationError(BaseModel):
    """Define the structure of the validation error"""

    location: Optional[ValidationErrorLocation] = None
    unexpectedVersion: Optional[ValidationErrorUnexpectedVersion] = None
    syntaxError: Optional[dict] = None
    emptySection: Optional[dict] = None


class ValidationResult(BaseModel):
    """Define the structure of the validation result"""

    success: bool
    errors: list[ValidationError]


def log_level_decorator(level):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Save the original logging level
            original_level = logging.getLogger().level
            # Set logging level to the specified level
            logging.getLogger().setLevel(level)
            try:
                # Execute the function
                return func(*args, **kwargs)
            finally:
                # Reset logging level to original
                logging.getLogger().setLevel(original_level)

        return wrapper

    return decorator
