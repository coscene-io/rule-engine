import re

from .condition import Condition, ThunkCondition

always = Condition.wrap(True)
identity = ThunkCondition(lambda item, scope: (item, scope))
msg = identity.msg
ts = identity.ts
topic = identity.topic
msgtype = identity.msgtype

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
    return condition.map_condition_value(lambda x: not x)

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
    return key.map_condition_value(
        lambda k: ThunkCondition(lambda item, scope: (scope[k], scope))
    )

@Condition.wrap_args
def set_value(key, value):
    return key.map_condition_value(
        lambda actual_key: value.map_condition_value(
            lambda actual_value: ThunkCondition(
                lambda item, scope: (True, {**scope, actual_key: actual_value})
            )
        )
    )

@Condition.wrap_args
def has(parent, child):
    return parent.map_condition_value(
        lambda p: child.map_condition_value(
            lambda c: ThunkCondition(
                lambda item, scope: (
                    c in p,
                    {**scope, "cos/contains": c if c in p else None},
                )
            )
        )
    )


def regex(value, pattern):
    return (
        Condition.wrap(value)
        .map_condition_value(lambda v: re.search(pattern, v))
        .map_condition_value(
            lambda match_result: ThunkCondition(
                lambda item, scope: (match_result, {**scope, "cos/regex": match_result})
            )
        )
    )


__all__ = [
    "always",
    "identity",
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
]
