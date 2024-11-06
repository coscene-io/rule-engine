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

from rule_engine.action import Action
from rule_engine.condition import Condition
from rule_engine.utils import (
    ErrorSectionEnum,
    ValidationError,
    ValidationErrorLocation,
    ValidationResult,
)


class Rule:
    """
    Defining a rule with a condition and corresponding actions
    """

    def __init__(
        self,
        conditions: list[Condition],
        actions: list[Action],
        scope: dict[str, str],
        topic: str,
    ):
        self.conditions = conditions
        self.actions = actions
        self.scope = scope
        self.topic = topic

    def compile_and_validate(self, rule_idx: int) -> list[ValidationError]:
        """
        Compile and validate the rule, returning a list of errors
        """
        errors = []
        if not self.conditions:
            errors.append(
                ValidationError(
                    location=ValidationErrorLocation(
                        ruleIndex=rule_idx, section=ErrorSectionEnum.CONDITION
                    ),
                    emptySection={},
                ),
            )
        if not self.actions:
            errors.append(
                ValidationError(
                    location=ValidationErrorLocation(
                        ruleIndex=rule_idx, section=ErrorSectionEnum.ACTION
                    ),
                    emptySection={},
                ),
            )

        for idx, condition in enumerate(self.conditions):
            if not condition.validation_result:
                errors.append(
                    ValidationError(
                        location=ValidationErrorLocation(
                            ruleIndex=rule_idx,
                            section=ErrorSectionEnum.CONDITION,
                            itemIndex=idx,
                        ),
                        syntaxError={},
                    ),
                )
        for idx, action in enumerate(self.actions):
            if not action.validation_result:
                errors.append(
                    ValidationError(
                        location=ValidationErrorLocation(
                            ruleIndex=rule_idx,
                            section=ErrorSectionEnum.ACTION,
                            itemIndex=idx,
                        ),
                        syntaxError={},
                    ),
                )
        return errors

    def evaluate_and_run(self, msg: dict[str, any], topic: str, ts: float):
        """Evaluate the rule conditions(connected by AND) and run the actions if all conditions are met"""
        if self.topic != topic:
            return

        activation = {
            "scope": celpy.adapter.json_to_cel(self.scope),
            "msg": celpy.adapter.json_to_cel(msg),
            "topic": celpy.celtypes.StringType(topic),
            "ts": celpy.celtypes.DoubleType(ts),
        }
        for condition in self.conditions:
            if not condition.evaluate(activation):
                return

        for action in self.actions:
            action.run(activation)


def validate_rules(rules: list[Rule]) -> ValidationResult:
    """
    Validate the rules
    """
    errors = []
    for idx, rule in enumerate(rules):
        errors += rule.compile_and_validate(idx)
    return ValidationResult(success=not errors, errors=errors)


def spec_to_rules(spec: dict[str, any], action_impls: dict[str, any]) -> list[Rule]:
    """
    Convert the spec to an engine
    """
    rules = []
    for rule_spec in spec.get("rules", []):
        conditions = []
        for condition_obj in rule_spec.get("condition_specs", []):
            conditions.append(_parse_condition(condition_obj))
        actions = []
        for action_obj in rule_spec.get("action_specs", []):
            actions.append(_parse_action(action_obj, action_impls))
        scopes = rule_spec.get("each", [])
        topic = rule_spec.get("active_topics", [""])[0]
        if not scopes:
            scopes = [{}]
        for scope in scopes:
            rules.append(Rule(conditions, actions, scope, topic))
    return rules


def _parse_condition(condition_obj: dict[str, any]) -> Condition:
    """
    Parse the condition object
    """
    raw_condition = condition_obj.get("raw", "")
    if raw_condition:
        return Condition(raw_condition)

    structured_condition = condition_obj.get("structured", {})
    path = structured_condition.get("path", "")
    op = structured_condition.get("op", "")
    value = structured_condition.get("value", "")
    type_ = structured_condition.get("type", "")
    return Condition(f"{type_}({path}) {op} {type_}({value})")


def _parse_action(action_obj: dict[str, any], action_impls: dict[str, any]) -> Action:
    """
    Parse the action object
    """
    name = action_obj.get("name", "")
    kwargs = action_obj.get("kwargs", {})
    impl = action_impls.get(name, lambda: None)
    return Action(name, impl, kwargs)
