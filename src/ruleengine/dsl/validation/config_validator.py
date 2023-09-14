from ruleengine.engine import Rule
from ruleengine.dsl.validation.validator import validate_action, validate_condition
from ruleengine.dsl.validation.validation_result import ValidationErrorType

ALLOWED_VERSIONS = ["v1"]


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
        rule_errors, new_rules = _validate_rule(rule, i, action_impls)
        errors += rule_errors
        rules += new_rules

    success = not bool(errors)
    return {"success": success, "errors": errors}, rules if success else None


def _validate_rule(rule, rule_index, action_impls):
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
    if errors:
        return errors, []

    templating_args = rule.get("each", [])
    if not templating_args:
        return [], [Rule(conditions, actions, {})]

    new_rules = []
    for arg in templating_args:
        conditions, actions = parse_rule()
        new_rules.append(Rule(conditions, actions, arg))
    return [], new_rules


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

        case ValidationErrorType.UNKNOWN:
            return {"genericError": {"msg": result.details["message"]}}
        case _:
            raise Exception(f"Unknown error type: {result.error_type}")
