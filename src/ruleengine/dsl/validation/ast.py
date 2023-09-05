import ast
from .validation_result import ValidationResult, ValidationErrorType


def validate_expression(expr_str, injected_values):
    try:
        parsed = ast.parse(expr_str, mode="eval")
    except SyntaxError:
        return ValidationResult(False, error_type=ValidationErrorType.SYNTAX)

    for node in ast.walk(parsed):
        match node:
            case ast.Name(name, _):
                if name not in injected_values:
                    return ValidationResult(
                        False, error_type=ValidationErrorType.UNDEFINED, details={"name": name}
                    )

    return ValidationResult(True)
