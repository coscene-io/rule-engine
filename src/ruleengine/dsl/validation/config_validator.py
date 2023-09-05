from sys import argv
import json
from ruleengine.dsl.validation.validator import validate_action, validate_condition
from ruleengine.dsl.validation.validation_result import ValidationErrorType

ALLOWED_VERSIONS = ["1", "1.0.0", "v1"]


def validate_config(config, action_impls):
    """
    Validate a rule specification.

    It is assumed that the input config is a DiagnosisRule specified in

    https://github.com/coscene-io/cosceneapis/blob/main/coscene/dataplatform/v1alpha2/common/diagnosis_rule.proto

    and this function will return a DiagnosisRuleValidationResult specified in

    https://github.com/coscene-io/cosceneapis/blob/main/coscene/dataplatform/v1alpha2/common/diagnosis_rule_validation_result.proto
    """

    # TODO: Instead of putting together these objects by hand, we should connect
    # the protos generated in cosceneapis

    if config["version"] not in ALLOWED_VERSIONS:
        return {
            "success": False,
            "errors": [{"unexpectedVersion": {"allowedVersions": ALLOWED_VERSIONS}}],
        }

    errors = []
    rules = []
    for i, rule in enumerate(config["rules"]):
        rule_errors, conditions, actions = _validate_rule(rule, i, action_impls)
        errors += rule_errors
        rules.append((conditions, actions))

    success = not bool(errors)
    return {"success": success, "errors": errors}, rules if success else None


def _validate_rule(rule, rule_index, action_impls):
    errors = []
    if not rule["when"]:
        errors.append(
            {
                "location": {
                    "ruleIndex": rule_index,
                    "section": 1,
                },
                "emptySection": {},
            }
        )
    if not rule["actions"]:
        errors.append(
            {
                "location": {
                    "ruleIndex": rule_index,
                    "section": 2,
                },
                "emptySection": {},
            }
        )

    conditions = []
    for i, cond_str in enumerate(rule["when"]):
        res = validate_condition(cond_str)
        if not res.success:
            errors.append(
                {
                    "location": {
                        "ruleIndex": rule_index,
                        "section": 1,
                        "itemIndex": i,
                    },
                    **_convert_to_json_error(res),
                }
            )
        else:
            conditions.append(res.entity)

    actions = []
    for i, action_str in enumerate(rule["actions"]):
        res = validate_action(action_str, action_impls)
        if not res.success:
            errors.append(
                {
                    "location": {
                        "ruleIndex": rule_index,
                        "section": 2,
                        "itemIndex": i,
                    },
                    **_convert_to_json_error(res),
                }
            )
        else:
            actions.append(res.entity)
    return errors, conditions, actions


def _convert_to_json_error(result):
    match result.error_type:
        case ValidationErrorType.SYNTAX | ValidationErrorType.EMPTY:
            return {"syntax_error": {}}

        case ValidationErrorType.NOT_CONDITION:
            return {"notCondition": {"actualType": result.details["actual"]}}
        case ValidationErrorType.NOT_ACTION:
            return {"notAction": {"actualType": result.details["actual"]}}

        case ValidationErrorType.UNDEFINED:
            return {"nameUndefined": {"name": result.details["name"]}}

        case ValidationErrorType.TYPE | ValidationErrorType.UNKNOWN:
            return {"genericError": {"msg": result.details["message"]}}
        case _:
            raise Exception(f"Unknown error type: {result.error_type}")
