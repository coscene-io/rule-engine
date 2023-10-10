import ast
from ruleengine.dsl.validation.normalizer import normalize_expression_tree
from ruleengine.dsl.validation.validator import base_dsl_values


def str_to_condition(expr_str, additional_injected_values=None):
    parsed = ast.parse(expr_str, mode="eval")
    code = compile(normalize_expression_tree(parsed), "", mode="eval")
    return eval(code, {**base_dsl_values, **(additional_injected_values or {})})
