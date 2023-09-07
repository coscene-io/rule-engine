import ast
from .validation_result import ValidationResult, ValidationErrorType
from .normalizer import normalize_expression_tree


def validate_expression(expr_str, injected_values):
    try:
        parsed = normalize_expression_tree(ast.parse(expr_str, mode="eval"))
    except SyntaxError:
        return ValidationResult(False, ValidationErrorType.SYNTAX)

    for node in ast.walk(parsed):
        match node:
            case ast.Name(name, _):
                if name not in injected_values:
                    return ValidationResult(
                        False, ValidationErrorType.UNDEFINED, {"name": name}
                    )

    code = compile(parsed, "", mode="eval")

    return ValidationResult(True, entity=eval(code, injected_values))

