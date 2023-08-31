import ast
import inspect
from ruleengine.dsl import base_conditions, log_conditions, sequence_conditions
from ruleengine.dsl.condition import Condition
from .validation_result import ValidationResult, ValidationErrorType
from .ast import validate_expression, ValidationException

base_dsl_values = dict(
    inspect.getmembers(base_conditions)
    + inspect.getmembers(log_conditions)
    + inspect.getmembers(sequence_conditions)
)


def upload(
    before=10,
    title="",
    description="",
    labels=[],
    extra_files=[],
):
    pass


def create_moment(
    title,
    description="",
    timestamp=0,
    duration=1,
    create_task=False,
    assign_to=None,
):
    pass


actions_dsl_values = {
    "upload": upload,
    "create_moment": create_moment,
    **base_dsl_values,
}


def validate_condition(cond_str):
    if not cond_str.strip():
        return ValidationResult(False, ValidationErrorType.EMPTY)

    expr_res = validate_expression(cond_str, base_dsl_values)
    if not expr_res.success:
        return expr_res

    result = eval(cond_str, base_dsl_values)

    if not isinstance(result, Condition):
        return ValidationResult(
            False, ValidationErrorType.NOT_CONDITION, {"actual": type(result).__name__}
        )

    return ValidationResult(True)


def validate_action(action_str):
    pass
