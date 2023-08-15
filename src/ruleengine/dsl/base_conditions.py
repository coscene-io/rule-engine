import re

from .condition import Condition, ThunkCondition

always = Condition.wrap(True)
identity = ThunkCondition(lambda item, scope: (item, scope))
msg = identity.msg
ts = identity.ts
topic = identity.topic
msgtype = identity.msgtype


def and_(*conditions):
    assert len(conditions) > 1, 'and_ must have at least 2 conditions'

    def new_thunk(item, scope):
        for condition in conditions[:-1]:
            value, scope = Condition.wrap(condition).evaluate_condition_at(item, scope)
            if not value:
                return value, scope
        return Condition.wrap(conditions[-1]).evaluate_condition_at(item, scope)

    return ThunkCondition(new_thunk)


def or_(*conditions):
    assert len(conditions) > 1, 'or_ must have at least 2 conditions'

    def new_thunk(item, scope):
        for condition in conditions[:-1]:
            value, scope = Condition.wrap(condition).evaluate_condition_at(item, scope)
            if value:
                return value, scope
        return Condition.wrap(conditions[-1]).evaluate_condition_at(item, scope)

    return ThunkCondition(new_thunk)


def not_(condition):
    return Condition.wrap(condition).map_condition_value(lambda x: not x)


def get_value(key):
    return Condition.wrap(key).map_condition_value(
        lambda k: ThunkCondition(lambda item, scope: (scope[k], scope)))


def set_value(key, value):
    return Condition.wrap(key).map_condition_value(
        lambda actual_key: Condition.wrap(value).map_condition_value(
            lambda actual_value: ThunkCondition(
                lambda item, scope: (True, {**scope, actual_key: actual_value}))))


def topic_is(name):
    return topic == name


def type_is(name):
    return msgtype == name


def has(parent, child):
    return Condition.wrap(parent).map_condition_value(
        lambda p: Condition.wrap(child).map_condition_value(
            lambda c: ThunkCondition(lambda item, scope: (c in p, {**scope, 'cos/contains': c if c in p else None}))))


def regex_search(value, pattern):
    return Condition.wrap(value).map_condition_value(
        lambda v: re.search(pattern, v)).map_condition_value(
        lambda match_result:
        ThunkCondition(lambda item, scope: (match_result, {**scope, 'cos/regex': match_result})))
