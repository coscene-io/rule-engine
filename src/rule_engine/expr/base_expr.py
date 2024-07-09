from typing import Callable

from rule_engine.expr.expr import Expr, aggregate_callbacks


@Expr.wrap_args
def and_(*exprs: any) -> Expr:
    """
    Returns an Expr that is True if all the given Exprs are True.
    Note that short-circuiting is used, so the Exprs are evaluated in order until one is False.

    Note exprs should all be of type Expr after wrapping.
    """
    assert len(exprs) > 0, "and_ must have at least 1 condition"

    callbacks: list[Callable[[dict], None]] = []
    res = True
    for expr in exprs:
        callbacks.append(expr.callback)
        res = expr.value
        if not res:
            return Expr(res, callback=aggregate_callbacks(callbacks))

    return Expr(res, callback=aggregate_callbacks(callbacks))


@Expr.wrap_args
def or_(*exprs: any) -> Expr:
    """
    Returns an Expr that is True if at least one of the given Exprs is True.
    Note that short-circuiting is used, so the Exprs are evaluated in order until one is True.

    Note exprs should all be of type Expr after wrapping.
    """
    assert len(exprs) > 0, "or_ must have at least 1 condition"

    callbacks: list[Callable[[dict], None]] = []
    res = False
    for expr in exprs:
        callbacks.append(expr.callback)
        res = expr.value
        if res:
            return Expr(res, callback=aggregate_callbacks(callbacks))

    return Expr(res, callback=aggregate_callbacks(callbacks))


@Expr.wrap_args
def not_(expr: any) -> Expr:
    """
    Returns the negation of the given Expr.

    Note expr should all be of type Expr after wrapping.
    """
    if expr.value:
        return Expr(False, callback=expr.callback)
    else:
        return Expr(True, callback=expr.callback)


@Expr.wrap_args
def has(parent: any, child: any) -> Expr:
    """
    Returns True if the parent contains the child.

    Note parent and child should all be of type Expr after wrapping.
    """
    return Expr(
        value=child.value in parent.value,
        callback=aggregate_callbacks([parent.callback, child.callback]),
    )


base_expr_values = dict(
    and_=and_,
    or_=or_,
    not_=not_,
    has=has,
)
