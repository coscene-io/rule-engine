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
import celpy.adapter

from rule_engine.action import Action
from rule_engine.condition import Condition
from rule_engine.utils import (
    ErrorSectionEnum,
    ValidationError,
    ValidationErrorLocation,
    ValidationResult,
)

ALLOWED_VERSIONS = ["v2"]


class Rule:
    """
    Defining a rule with a condition and corresponding actions

    RuleSpec should be of the following structure:
    {
        "version": "v2",
        "rules": [
            {
                "conditions": [
                    "msg['temperature'] > 20",
                    "int(msg['humidity']) < int(30)"
                ],
                "actions: [
                    {
                        "name": "action_1",
                        "kwargs": {
                            "arg1_1": "{msg['item']}",
                            "arg1_2": 1
                        }
                    },
                    {
                        "name": "action_2",
                        "kwargs": {
                            "arg2_1": "{msg.code}",
                            "arg2_2": 1
                        }
                    }
                ],
                "scopes": [
                    {
                        "scope_key_a": "scope_value_a_1"
                        "scope_key_b": "scope_value_b_1"
                    },
                    {
                        "scope_key_a": "scope_value_a_2"
                        "scope_key_b": "scope_value_b_2"
                    }
                ],
                "topics": ["topic_1", "topic_2"]
            }
        ]
    }
    Note that for each scope item will be used to construct a separate rule,
    In the above example, two rules will be created with the same conditions and actions and topics,
    but with one scope being {"scope_key_a": "scope_value_a_1", "scope_key_b": "scope_value_b_1"}
    and the other being {"scope_key_a": "scope_value_a_2", "scope_key_b": "scope_value_b_2"}
    Also be aware that the rule_idx of scope created rules will be the same as the original rule
    """

    def __init__(
        self,
        raw: any,
        conditions: list[Condition],
        actions: list[Action],
        scope: dict[str, str],
        topics: list[str],
        rule_idx: int = 0,  # the index of the rule in the rule set, used for validation error reporting
        metadata: dict[str, any] = None,  # user-defined metadata
    ):
        self.raw = raw
        self.conditions = conditions
        self.actions = actions
        self.scope = celpy.adapter.json_to_cel(scope)
        self.topics = topics
        self.rule_idx = rule_idx
        self.metadata = metadata or {}

    def get_validation_errors(self) -> list[ValidationError]:
        """
        Compile and validate the rule, returning a list of errors

        rule_idx: the index of the rule in the rule set
        """
        errors = []
        if not self.conditions:
            errors.append(
                ValidationError(
                    location=ValidationErrorLocation(
                        ruleIndex=self.rule_idx, section=ErrorSectionEnum.CONDITION
                    ),
                    emptySection={},
                ),
            )
        if not self.actions:
            errors.append(
                ValidationError(
                    location=ValidationErrorLocation(
                        ruleIndex=self.rule_idx, section=ErrorSectionEnum.ACTION
                    ),
                    emptySection={},
                ),
            )

        for idx, condition in enumerate(self.conditions):
            if not condition.validation_result:
                errors.append(
                    ValidationError(
                        location=ValidationErrorLocation(
                            ruleIndex=self.rule_idx,
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
                            ruleIndex=self.rule_idx,
                            section=ErrorSectionEnum.ACTION,
                            itemIndex=idx,
                        ),
                        syntaxError={},
                    ),
                )
        return errors


def validate_rules(rules: list[Rule]) -> ValidationResult:
    """
    Validate the rules
    """
    errors = []
    for idx, rule in enumerate(rules):
        errors += rule.get_validation_errors()
    return ValidationResult(success=not errors, errors=errors)


def spec_to_rules(spec: dict[str, any], action_impls: dict[str, any]) -> list[Rule]:
    """
    Convert the spec to an engine, mainly used to validate a json-formed rule set.
    """
    rules = []
    for rule_idx, rule_spec in enumerate(spec.get("rules", [])):
        conditions = [
            Condition(condition_spec)
            for condition_spec in rule_spec.get("conditions", [])
        ]

        actions = []
        for action_obj in rule_spec.get("actions", []):
            action_name = action_obj.get("name", "")
            action_kwargs = action_obj.get("kwargs", {})
            action_impl = action_impls.get(action_name)
            actions.append(Action(action_name, action_kwargs, action_impl))

        scopes = rule_spec.get("scopes", [])
        topics = rule_spec.get("topics", [])
        if not scopes:
            scopes = [{}]
        for scope in scopes:
            rules.append(Rule(rule_spec, conditions, actions, scope, topics, rule_idx))
    return rules
