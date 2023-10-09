import inspect
import ast
from ruleengine.dsl import base_conditions, log_conditions, sequence_conditions
from ruleengine.dsl.validation.normalizer import normalize_expression_tree

base_dsl_values = dict(
    inspect.getmembers(base_conditions)
    + inspect.getmembers(log_conditions)
    + inspect.getmembers(sequence_conditions)
)


def str_to_condition(expr_str, additional_injected_values=None):
    parsed = ast.parse(expr_str, mode="eval")
    code = compile(normalize_expression_tree(parsed), "", mode="eval")
    return eval(code, {**base_dsl_values, **(additional_injected_values or {})})
