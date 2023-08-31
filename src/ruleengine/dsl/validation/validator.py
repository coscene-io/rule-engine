import ast
import inspect
from ruleengine.dsl import base_conditions, log_conditions, sequence_conditions
from ruleengine.dsl.condition import Condition
from ruleengine.dsl.action import Action
from .validation_result import ValidationResult, ValidationErrorType
from .ast import validate_expression, ValidationException
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
    return _do_validate(cond_str, base_dsl_values, Condition)


def validate_action(action_str):
    return _do_validate(cond_str, actions_dsl_values, Action)

def _do_validate(expr_str, injected_values, expected_class):
    if not expr_str.strip():
        return ValidationResult(False, ValidationErrorType.EMPTY)

    expr_res = validate_expression(expr_str, injected_values)
    if not expr_res.success:
        return expr_res

    result = eval(expr_str, injected_values)

    if not isinstance(result, expected_class):
        return ValidationResult(
            False, ValidationErrorType.NOT_CONDITION, {"actual": type(result).__name__}
        )

    return ValidationResult(True)

