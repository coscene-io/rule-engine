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

from ruleengine.dsl.validation.normalizer import normalize_expression_tree
from ruleengine.dsl.validation.validator import base_dsl_values


def str_to_condition(expr_str, additional_injected_values=None):
    parsed = ast.parse(expr_str, mode="eval")
    code = compile(normalize_expression_tree(parsed), "", mode="eval")
    return eval(code, {**base_dsl_values, **(additional_injected_values or {})})
