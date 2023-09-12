import inspect
from ruleengine.dsl import base_conditions, log_conditions, sequence_conditions
from ruleengine.dsl.condition import Condition
from ruleengine.dsl.action import Action
from .validation_result import ValidationResult, ValidationErrorType
from .ast import validate_expression
from .actions import ActionValidator, UnknownFunctionKeywordArgException

base_dsl_values = dict(
    inspect.getmembers(base_conditions)
    + inspect.getmembers(log_conditions)
    + inspect.getmembers(sequence_conditions)
)


def validate_condition(cond_str):
    return _do_validate(
        cond_str, base_dsl_values, Condition, ValidationErrorType.NOT_CONDITION
    )


def validate_action(action_str, action_impls):
    action_validator = ActionValidator(action_impls)
    action_dsl_values = {
        "upload": action_validator.upload,
        "create_moment": action_validator.create_moment,
        **base_dsl_values,
    }
    return _do_validate(
        action_str,
        action_dsl_values,
        Action,
        ValidationErrorType.NOT_ACTION,
    )


def _do_validate(expr_str, injected_values, expected_class, class_expectation_error):
    if not expr_str.strip():
        return ValidationResult(False, ValidationErrorType.EMPTY)

    try:
        res = validate_expression(expr_str, injected_values)
        if not res.success:
            return res
    except UnknownFunctionKeywordArgException as e:
        return ValidationResult(False, ValidationErrorType.UNDEFINED, {"name": e.name})
    except Exception as e:
        return ValidationResult(False, ValidationErrorType.UNKNOWN, {"message": str(e)})

    if not isinstance(res.entity, expected_class):
        return ValidationResult(
            False, class_expectation_error, {"actual": type(res.entity).__name__}
        )

    return res
