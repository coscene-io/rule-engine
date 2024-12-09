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
import celpy

from rule_engine.utils import ENV


class Condition:
    """
    Defining a condition with a CEL expression
    """

    @staticmethod
    def compile_and_validate(raw_condition: str):
        """
        Validate the condition
        """
        try:
            program = ENV.program(ENV.compile(raw_condition))
            return Condition(raw_condition, program), None
        except Exception as e:
            return None, e

    def __init__(self, raw: str, program: celpy.Runner):
        self.raw = raw
        self.program = program

    def evaluate(self, activation: celpy.Context):
        """
        Evaluate the condition as boolean
        """
        try:
            # Restrict the return to be true when the condition evaluates exactly to boolean true
            return self.program.evaluate(activation).__repr__() == "BoolType(True)"
        except Exception:
            return False

    def __repr__(self):
        return f"Condition({self.raw})"

    def __str__(self):
        return f"Condition({self.raw})"
