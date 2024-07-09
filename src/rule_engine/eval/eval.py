import ast

from rule_engine.eval.ast_transformer import AstTransformer
from rule_engine.expr.base_expr import and_, or_
from rule_engine.expr.expr import Expr


def inject_item_values(item_raw: any, base_injected_values: dict) -> dict:
    """
    Injects item related values into the context of the expression evaluation
    Here we are injecting self defined values into the context including
    the item, msg, ts, topic, msgtype, log
    """
    item = Expr(item_raw)
    msg = item.msg
    ts = item.ts
    topic = item.topic
    msgtype = item.msgtype

    _is_foxglove = or_(msgtype == "foxglove_msgs/Log", msgtype == "foxglove.Log")
    _is_ros = msgtype == "rosgraph_msgs/Log"
    log = or_(and_(_is_ros, msg.msg), and_(_is_foxglove, msg.message), Expr(""))

    return {
        "item": item,
        "msg": msg,
        "ts": ts,
        "topic": topic,
        "msgtype": msgtype,
        "log": log,
        "map": map,
        **base_injected_values,
    }


def parse_expr(expr_str: str) -> ast.Expression:
    """
    Parses an expression string into an AST expression
    """
    return ast.parse(expr_str, mode="eval")


def eval_expression(parsed_expr: ast.Expression, injected_values: dict, ctx: dict) -> any:
    """
    Evaluates an expression with the injected values
    """
    for node in ast.walk(parsed_expr):
        if isinstance(node, ast.Name):
            name = node.id
            if name not in injected_values:
                raise SyntaxError(f"NameError: name '{name}' is not defined")

    code = compile(
        ast.fix_missing_locations(AstTransformer().visit(parsed_expr)), "", mode="eval"
    )

    res = eval(code, injected_values)
    if isinstance(res, Expr):
        return res.eval(ctx)
    else:
        return res
