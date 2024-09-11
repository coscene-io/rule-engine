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

import copy

from ruleengine.dsl.validation.validation_result import ValidationErrorType
from ruleengine.dsl.validation.validator import validate_action, validate_condition
from ruleengine.engine import Rule

ALLOWED_VERSIONS = ["v1"]


def validate_config(config, action_impls, project_name=""):
    """
    Validate a rule specification. Use validate_config_wrapped instead if action_impls depends on the rule.

    It is assumed that the input config is a DiagnosisRule specified in

    https://github.com/coscene-io/cosceneapis/blob/main/coscene/dataplatform/v1alpha2/common/diagnosis_rule.proto

    and this function will return a DiagnosisRuleValidationResult specified in

    https://github.com/coscene-io/cosceneapis/blob/main/coscene/dataplatform/v1alpha2/common/diagnosis_rule_validation_result.proto

    :param config: The rule specification.
    :param action_impls: A dictionary of action implementations.
    :param project_name: The name of the project that the rule is associated with.
    """
    action_impls_wrapped = {k: lambda _: v for k, v in action_impls.items()}
    return validate_config(config, action_impls_wrapped, project_name)


def validate_config_wrapped(config, action_impls_wrapped, project_name=""):
    """
    Validate a rule specification where the action implementations depend on the rule.
    """

    # TODO: Instead of putting together these objects by hand, we should connect
    # the protos generated in cosceneapis

    raw_version = config.get("version", "")
    raw_rules = config.get("rules", [])

    if raw_version not in ALLOWED_VERSIONS:
        return {
            "success": False,
            "errors": [{"unexpectedVersion": {"allowedVersions": ALLOWED_VERSIONS}}],
        }, []

    errors = []
    rules = []
    for i, rule in enumerate(raw_rules):
        action_impls = {k: v(rule) for k, v in action_impls_wrapped.items()}
        rule_errors, new_rules = _validate_rule(rule, i, action_impls, project_name)
        errors += rule_errors
        rules += new_rules

    success = not bool(errors)
    return {"success": success, "errors": errors}, rules


def _validate_rule(rule, rule_index, action_impls, project_name):
    errors = []
    raw_conditions = rule.get("when", [])
    raw_actions = rule.get("actions", [])
    if not raw_conditions:
        errors.append(
            {
                "location": {
                    "ruleIndex": rule_index,
                    "section": 1,
                },
                "emptySection": {},
            }
        )
    if not raw_actions:
        errors.append(
            {
                "location": {
                    "ruleIndex": rule_index,
                    "section": 2,
                },
                "emptySection": {},
            }
        )

    def parse_rule():
        conditions = []
        for i, cond_str in enumerate(raw_conditions):
            res = validate_condition(cond_str)
            if not res.success:
                errors.append(
                    {
                        "location": {
                            "ruleIndex": rule_index,
                            "section": 1,
                            "itemIndex": i,
                            "details": res.details,
                        },
                        **_convert_to_json_error(res),
                    }
                )
            else:
                conditions.append(res.entity)

        actions = []
        for i, action_str in enumerate(raw_actions):
            res = validate_action(action_str, action_impls)
            if not res.success:
                errors.append(
                    {
                        "location": {
                            "ruleIndex": rule_index,
                            "section": 2,
                            "itemIndex": i,
                            "details": res.details,
                        },
                        **_convert_to_json_error(res),
                    }
                )
            else:
                actions.append(res.entity)
        return conditions, actions

    # We parse the rules once to see if there are any errors. If so, bail. Also,
    # if there are no `each` values, we use this set of parsed values for the
    # actual execution.
    #
    # If there are `each` values, we parse a new set of rules for each of them,
    # since rules are stateful, so we want separate instances.

    conditions, actions = parse_rule()
    upload_limit = rule.get("upload_limit", {})
    if errors:
        return errors, []

    templating_args = rule.get("each", [])
    if not templating_args:
        return [], [
            Rule(
                conditions, actions, {}, upload_limit, copy.deepcopy(rule), project_name
            )
        ]

    new_rules = []
    for arg in templating_args:
        conditions, actions = parse_rule()
        new_rules.append(
            Rule(
                conditions,
                actions,
                arg,
                upload_limit,
                {**copy.deepcopy(rule), "each": [arg]},
                project_name,
            )
        )
    return [], new_rules


def _convert_to_json_error(result):
    if result.error_type == ValidationErrorType.SYNTAX or ValidationErrorType.EMPTY:
        return {"syntax_error": {}}
    elif result.error_type == ValidationErrorType.NOT_CONDITION:
        return {"notCondition": {"actualType": result.details["actual"]}}
    elif result.error_type == ValidationErrorType.NOT_ACTION:
        return {"notAction": {"actualType": result.details["actual"]}}
    elif result.error_type == ValidationErrorType.UNDEFINED:
        return {"nameUndefined": {"name": result.details["name"]}}
    elif result.error_type == ValidationErrorType.UNKNOWN:
        return {"genericError": {"msg": result.details["message"]}}
    else:
        raise Exception(f"Unknown error type: {result.error_type}")
