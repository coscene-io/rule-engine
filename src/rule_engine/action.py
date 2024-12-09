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
import re
from functools import partial
from typing import Callable

import celpy

from rule_engine.utils import ENV


class Action:
    """
    Defining an action, of which the underlying implementation is a function
    """

    @staticmethod
    def compile_and_validate(name: str, raw_kwargs: dict[str, any], impl: Callable):
        """
        Compile and validate the action
        """
        try:
            kwargs = {k: compile_value(v) for k, v in raw_kwargs.items()}
            return Action(name, raw_kwargs, kwargs, impl), None
        except Exception as e:
            return None, e

    def __init__(
        self,
        name: str,
        raw_kwargs: dict[str, any],
        kwargs: dict[str, Callable[[celpy.Context], any]],
        impl: Callable,
    ):
        self.name = name
        self.raw_kwargs = raw_kwargs
        self._impl = impl
        self._kwargs = kwargs

    def run(self, activation: celpy.Context):
        """
        Run the action with the activation dictionary
        """
        self._impl(**{k: v(activation) for k, v in self._kwargs.items()})

    def __repr__(self):
        return f"Action({self.name}){self.raw_kwargs}"


def compile_value(value: any) -> Callable[[celpy.Context], any]:
    """
    Compile a value, which can be a string that optionally with embedded CEL expression,
    or otherwise a constant value
    """
    if isinstance(value, str):
        return compile_embedded_expr(value)
    elif isinstance(value, dict):
        compiled_value = {}
        for k, v in value.items():
            if isinstance(v, dict):
                raise ValueError("Nested dict is not supported")
            compiled_value[k] = compile_value(v)

        def evaluate_dict(activation: celpy.Context, _value: dict):
            return {_k: _v(activation) for _k, _v in _value.items()}

        return partial(evaluate_dict, _value=compiled_value)

    else:

        def wrap(_value):
            return lambda _: _value

        return wrap(value)


def compile_embedded_expr(expr: str) -> Callable[[celpy.Context], str]:
    """
    Compile a string with optional embedded CEL expression, for example:
    expression: "aaa { msg.code } bbb { msg.error } {msg.aaa}"
    activation: {"msg": {"code": "404", "error": "Not found"}}
    result: "aaa 404 bbb Not found { ERROR }"

    The evaluation process is done by evaluating all the CEL expression enclosed in {{ and }} and
    replacing the expression with the evaluated value. (Trim pre- and post- spaces in between {{ and }})

    Returns a function that takes an activation dictionary and returns the evaluated string
    """
    pattern = re.compile(r"\{\s*(.*?)\s*}")
    matches = pattern.findall(expr)
    compiled_programs = [ENV.program(ENV.compile(match)) for match in matches]

    def evaluate(
        activation: celpy.Context, expression: str, programs: list[celpy.Runner]
    ) -> str:
        # Replace the matches in the expression with the evaluated value
        idx = -1

        def replace(_match):
            nonlocal idx
            idx += 1
            try:
                return str(programs[idx].evaluate(activation))
            except Exception:
                return "{ ERROR }"

        return re.sub(pattern, replace, expression)

    return partial(evaluate, expression=expr, programs=compiled_programs)
