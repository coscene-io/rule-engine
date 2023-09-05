import inspect
from ruleengine.dsl import base_conditions, log_conditions, sequence_conditions
from ruleengine.dsl.condition import Condition
from ruleengine.dsl.action import Action
from .validation_result import ValidationResult, ValidationErrorType
from .ast import validate_expression
from . import fake_actions

base_dsl_values = dict(
    inspect.getmembers(base_conditions)
    + inspect.getmembers(log_conditions)
    + inspect.getmembers(sequence_conditions)
)

actions_dsl_values = {
    **dict(inspect.getmembers(fake_actions)),
    **base_dsl_values,
}


def validate_condition(cond_str):
    return _do_validate(
        cond_str, base_dsl_values, Condition, ValidationErrorType.NOT_CONDITION
    )


def validate_action(action_str):
    return _do_validate(
        action_str, actions_dsl_values, Action, ValidationErrorType.NOT_ACTION
    )


def _do_validate(expr_str, injected_values, expected_class, class_expectation_error):
    if not expr_str.strip():
        return ValidationResult(False, error_type=ValidationErrorType.EMPTY)

    expr_res = validate_expression(expr_str, injected_values)
    if not expr_res.success:
        return expr_res

    try:
        result = eval(expr_str, injected_values)
    except TypeError as e:
        return ValidationResult(False, error_type=ValidationErrorType.TYPE, details={"message": str(e)})
    except Exception as e:
        return ValidationResult(False, error_type=ValidationErrorType.UNKNOWN, details={"message": str(e)})

    if not isinstance(result, expected_class):
        return ValidationResult(
            False, error_type=class_expectation_error, details={"actual": type(result).__name__}
        )

    return ValidationResult(True)
