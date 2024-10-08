# Copyright 2024 coScene
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

from .condition import Condition, ThunkCondition, get_attr_or_item

always = Condition.wrap(True)
msg = ThunkCondition(lambda item, scope: (item.msg, scope))
ts = ThunkCondition(lambda item, scope: (item.ts, scope))
topic = ThunkCondition(lambda item, scope: (item.topic, scope))
msgtype = ThunkCondition(lambda item, scope: (item.msgtype, scope))


def get_start_time(item, scope):
    value = item.ts
    if "start_time" in scope:
        value = scope["start_time"]
    return value, scope


condition_start_time = ThunkCondition(get_start_time)


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
        key,
        lambda k: ThunkCondition(
            lambda item, scope: (scope[k], scope) if k in scope else (None, scope)
        ),
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


def map_attr(value, attr):
    def mapper(x):
        try:
            iter(x)
        except TypeError:
            return None
        result = [get_attr_or_item(attr)(v) for v in x]
        return result

    return Condition.map(Condition.wrap(value), mapper)


def func_apply(func, *args):
    return Condition.apply(
        lambda scope, f, *a: (f(*a), scope),
        Condition.wrap(func),
        *[Condition.wrap(arg) for arg in args]
    )


__all__ = [
    "always",
    "msg",
    "ts",
    "topic",
    "msgtype",
    "condition_start_time",
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
    "map_attr",
]
