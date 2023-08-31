import ast

class ValidationException(Exception):
    pass

def validate_expression(expr_str, injected_values):
    for node in ast.walk(ast.parse(expr_str, mode="eval")):
        print(node)

