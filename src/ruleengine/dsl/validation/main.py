from sys import argv
import json
from ruleengine.dsl.validation.validator import validate_action, validate_condition
from ruleengine.dsl.validation.validation_result import ValidationErrorType

ALLOWED_VERSIONS = ["1", "1.0.0"]


def validate_config(config):
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
    for i, rule in enumerate(config["rules"]):
        errors += validate_rule(rule, i)
    return {"success": not bool(errors), "errors": errors}


def validate_rule(rule, rule_index):
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
                    **convert_to_json_error(res),
                }
            )

    for i, action_str in enumerate(rule["actions"]):
        res = validate_action(action_str)
        if not res.success:
            errors.append(
                {
                    "location": {
                        "ruleIndex": rule_index,
                        "section": 2,
                        "itemIndex": i,
                    },
                    **convert_to_json_error(res),
                }
            )
    return errors


def convert_to_json_error(result):
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


if __name__ == "__main__":
    config = json.loads(argv[1])
    result = validate_config(config)

    print(json.dumps(result))
    exit(0 if result["success"] else 1)
