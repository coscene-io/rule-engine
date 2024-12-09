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
        metadata: dict[str, any] = None,  # user-defined metadata
    ):
        self.raw = raw
        self.conditions = conditions
        self.actions = actions
        self.scope = celpy.adapter.json_to_cel(scope)
        self.topics = topics
        self.metadata = metadata or {}


def validate_rules_spec(
    rules_spec: dict[str, any], action_impls: dict[str, any]
) -> tuple[list[Rule], ValidationResult]:
    """
    Validate rules spec, this function will only validate the structure of the rules spec
    """
    all_rules = []
    errors = []
    for rule_idx, rule_spec in enumerate(rules_spec.get("rules", [])):
        rules, errs = validate_rule_spec(rule_spec, action_impls, rule_idx)
        all_rules.extend(rules)
        errors.extend(errs)

    return all_rules, ValidationResult(success=not errors, errors=errors)


def validate_rule_spec(
    rule_spec: dict[str, any], action_impls: dict[str, any], rule_idx: int
) -> tuple[list[Rule], list[ValidationError]]:
    """
    Validate single rule spec
    """
    errors: list[ValidationError] = []

    if not rule_spec.get("conditions", []):
        errors.append(
            ValidationError(
                location=ValidationErrorLocation(
                    ruleIndex=rule_idx, section=ErrorSectionEnum.CONDITION
                ),
                emptySection={},
            ),
        )

    conditions = []
    for condition_idx, condition_spec in enumerate(rule_spec.get("conditions", [])):
        condition, err = Condition.compile_and_validate(condition_spec)
        if err:
            errors.append(
                ValidationError(
                    location=ValidationErrorLocation(
                        ruleIndex=rule_idx,
                        section=ErrorSectionEnum.CONDITION,
                        itemIndex=condition_idx,
                    ),
                    syntaxError={},
                ),
            )
        else:
            conditions.append(condition)

    if not rule_spec.get("actions", []):
        errors.append(
            ValidationError(
                location=ValidationErrorLocation(
                    ruleIndex=rule_idx, section=ErrorSectionEnum.ACTION
                ),
                emptySection={},
            ),
        )

    actions = []
    for action_idx, action_spec in enumerate(rule_spec.get("actions", [])):
        action_name = action_spec.get("name", "")
        action_kwargs = action_spec.get("kwargs", {})
        action_impl = action_impls.get(action_name)
        action, err = Action.compile_and_validate(
            action_name, action_kwargs, action_impl
        )
        if err:
            errors.append(
                ValidationError(
                    location=ValidationErrorLocation(
                        ruleIndex=rule_idx,
                        section=ErrorSectionEnum.ACTION,
                        itemIndex=action_idx,
                    ),
                    syntaxError={},
                ),
            )
        else:
            actions.append(action)

    if errors:
        return [], errors

    scopes = rule_spec.get("scopes", [])
    topics = rule_spec.get("topics", [])
    if not scopes:
        scopes = [{}]

    rules = []
    for scope in scopes:
        rules.append(Rule(rule_spec, conditions, actions, scope, topics))

    return rules, []
