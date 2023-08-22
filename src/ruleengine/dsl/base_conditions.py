import re

from .condition import Condition, ThunkCondition

always = Condition.wrap(True)
identity = ThunkCondition(lambda item, scope: (item, scope))
msg = identity.msg
ts = identity.ts
topic = identity.topic
msgtype = identity.msgtype


def and_(*conditions):
    assert len(conditions) > 0, "and_ must have at least 1 condition"

    def new_thunk(item, scope):
        value = True
        for condition in conditions:
            value, scope = Condition.wrap(condition).evaluate_condition_at(item, scope)
            if not value:
                break
        return value, scope

    return ThunkCondition(new_thunk)


def or_(*conditions):
    assert len(conditions) > 0, "or_ must have at least 1 condition"

    def new_thunk(item, scope):
        value = False
        for condition in conditions:
            value, scope = Condition.wrap(condition).evaluate_condition_at(item, scope)
            if value:
                break
        return value, scope

    return ThunkCondition(new_thunk)


def not_(condition):
    return Condition.wrap(condition).map_condition_value(lambda x: not x)


def is_none(condition):
    def new_thunk(item, scope):
        value, scope = Condition.wrap(condition).evaluate_condition_at(item, scope)
        return value is None, scope

    return ThunkCondition(new_thunk)


def concat(*pieces):
    def new_thunk(item, scope):
        str_pieces = []
        for p in pieces:
            value, scope = Condition.wrap(p).evaluate_condition_at(item, scope)
            str_pieces.append(str(value))
        return "".join(str_pieces), scope

    return ThunkCondition(new_thunk)


def get_value(key):
    return Condition.wrap(key).map_condition_value(
        lambda k: ThunkCondition(lambda item, scope: (scope[k], scope))
    )


def set_value(key, value):
    return Condition.wrap(key).map_condition_value(
        lambda actual_key: Condition.wrap(value).map_condition_value(
            lambda actual_value: ThunkCondition(
                lambda item, scope: (True, {**scope, actual_key: actual_value})
            )
        )
    )


def topic_is(name):
    return topic == name


def type_is(name):
    return msgtype == name


def has(parent, child):
    return Condition.wrap(parent).map_condition_value(
        lambda p: Condition.wrap(child).map_condition_value(
            lambda c: ThunkCondition(
                lambda item, scope: (
                    c in p,
                    {**scope, "cos/contains": c if c in p else None},
                )
            )
        )
    )


def regex_search(value, pattern):
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
    "topic_is",
    "type_is",
    "has",
    "regex_search",
    "is_none",
]
