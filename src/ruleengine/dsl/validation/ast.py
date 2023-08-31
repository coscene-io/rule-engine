import ast
from .validation_result import ValidationResult, ValidationErrorType

class ValidationException(Exception):
    pass

def validate_expression(expr_str, injected_values):
    try:
        parsed = ast.parse(expr_str, mode="eval")
    except SyntaxError:
        return ValidationResult(False, ValidationErrorType.SYNTAX)

    for node in ast.walk(parsed):
        print(node)

    return ValidationResult(True)
