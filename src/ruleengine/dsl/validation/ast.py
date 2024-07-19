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

import ast

from .normalizer import normalize_expression_tree
from .validation_result import ValidationErrorType, ValidationResult


def validate_expression(expr_str, injected_values):
    try:
        parsed = ast.parse(expr_str, mode="eval")
    except SyntaxError:
        return ValidationResult(False, ValidationErrorType.SYNTAX)

    for node in ast.walk(parsed):
        if isinstance(node, ast.Name):
            name = node.id
            if name not in injected_values:
                return ValidationResult(
                    False, ValidationErrorType.UNDEFINED, {"name": name}
                )

    code = compile(normalize_expression_tree(parsed), "", mode="eval")

    return ValidationResult(True, entity=eval(code, injected_values))
