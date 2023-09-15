import re

from .condition import Condition, ThunkCondition

always = Condition.wrap(True)
msg = ThunkCondition(lambda item, scope: (item.msg, scope))
ts = ThunkCondition(lambda item, scope: (item.ts, scope))
topic = ThunkCondition(lambda item, scope: (item.topic, scope))
msgtype = ThunkCondition(lambda item, scope: (item.msgtype, scope))


@Condition.wrap_args
def and_(*conditions):
    assert len(conditions) > 0, "and_ must have at least 1 condition"

    def new_thunk(item, scope):
        value = True
        for condition in conditions:
            value, scope = condition.evaluate_condition_at(item, scope)
            if not value:
                break
        return value, scope

    return ThunkCondition(new_thunk)


@Condition.wrap_args
def or_(*conditions):
    assert len(conditions) > 0, "or_ must have at least 1 condition"

    def new_thunk(item, scope):
        value = False
        for condition in conditions:
            value, scope = condition.evaluate_condition_at(item, scope)
            if value:
                break
        return value, scope

    return ThunkCondition(new_thunk)


@Condition.wrap_args
def not_(condition):
    return Condition.map(condition, lambda x: not x)


@Condition.wrap_args
def is_none(condition):
    def new_thunk(item, scope):
        value, scope = condition.evaluate_condition_at(item, scope)
        return value is None, scope

    return ThunkCondition(new_thunk)


@Condition.wrap_args
def concat(*pieces):
    def new_thunk(item, scope):
        str_pieces = []
        for p in pieces:
            value, scope = p.evaluate_condition_at(item, scope)
            str_pieces.append(str(value))
        return "".join(str_pieces), scope

    return ThunkCondition(new_thunk)


@Condition.wrap_args
def get_value(key):
    return Condition.flatmap(
        key, lambda k: ThunkCondition(lambda item, scope: (scope[k], scope))
    )


@Condition.wrap_args
def set_value(key, value):
    return Condition.apply(
        lambda scope, actual_key, actual_value: (
            True,
            {**scope, actual_key: actual_value},
        ),
        key,
        value,
    )


@Condition.wrap_args
def has(parent, child):
    return Condition.apply(
        lambda scope, p, c: (c in p, {**scope, "cos/contains": c if c in p else None}),
        parent,
        child,
    )


def regex(value, pattern):
    return Condition.flatmap(
        Condition.map(Condition.wrap(value), lambda v: re.search(pattern, v)),
        lambda match_result: ThunkCondition(
            lambda item, scope: (match_result, {**scope, "cos/regex": match_result})
        ),
    )


def func_apply(func, *args):
    return Condition.apply(func, *[Condition.wrap(arg) for arg in args])


__all__ = [
    "always",
    "msg",
    "ts",
    "topic",
    "msgtype",
    "and_",
    "or_",
    "not_",
    "concat",
    "get_value",
    "set_value",
    "has",
    "regex",
    "is_none",
    "func_apply",
]
