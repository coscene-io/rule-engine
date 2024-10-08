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

import operator as op
from abc import ABC, abstractmethod
from functools import wraps


class Condition(ABC):
    """
    Defines a condition to be evaluated on a single message.

    It is assumed that the message has three fields, mirroring those of the ROS
    bag reader API:

    - topic
    - msg
    - msgtype
    - ts

    To make the DSL look nice at the end, this class ends up taking on a lot of
    the complexity. If you're familiar with monads, this class is a combination
    of Future and State and Optional.

    If you're not familiar with monads, this is going to be very confusing. I'm
    sorry.

    """

    @abstractmethod
    def evaluate_condition_at(self, item, scope):
        pass

    @staticmethod
    def wrap(value):
        if isinstance(value, Condition):
            return value
        return ThunkCondition(lambda item, scope: (value, scope))

    @staticmethod
    def wrap_args(func):
        """Decorator that calls wrap on all the args of a function."""

        @wraps(func)
        def result_func(*args, **kwargs):
            args = [Condition.wrap(value) for value in args]
            kwargs = {key: Condition.wrap(value) for key, value in kwargs.items()}
            return func(*args, **kwargs)

        return result_func

    @staticmethod
    def flatmap(self, mapper):
        def new_thunk(item, scope):
            value1, scope = self.evaluate_condition_at(item, scope)
            if value1 is None:
                return value1, scope

            return mapper(value1).evaluate_condition_at(item, scope)

        return ThunkCondition(new_thunk)

    @staticmethod
    def map(self, mapper):
        return MappedCondition(self, mapper)

    @staticmethod
    def apply(func, *args):
        def new_thunk(item, scope):
            new_args = []
            for arg in args:
                v, scope = arg.evaluate_condition_at(item, scope)
                if v is None:
                    return None, scope
                new_args.append(v)
            return func(scope, *new_args)

        return ThunkCondition(new_thunk)

    def __eq__(self, other):
        return self.__wrap_binary_op(other, op.eq)

    def __ne__(self, other):
        return self.__wrap_binary_op(other, op.ne)

    def __gt__(self, other):
        return self.__wrap_binary_op(other, op.gt, float)

    def __ge__(self, other):
        return self.__wrap_binary_op(other, op.ge, float)

    def __lt__(self, other):
        return self.__wrap_binary_op(other, op.lt, float)

    def __le__(self, other):
        return self.__wrap_binary_op(other, op.le, float)

    def __neg__(self):
        return Condition.map(self, op.neg)

    def __pos__(self):
        return Condition.map(self, op.pos)

    def __add__(self, other):
        return self.__wrap_binary_op(other, op.add, float)

    def __radd__(self, other):
        return self.__wrap_binary_op(other, op.add, float, True)

    def __sub__(self, other):
        return self.__wrap_binary_op(other, op.sub, float)

    def __rsub__(self, other):
        return self.__wrap_binary_op(other, op.sub, float, True)

    def __mul__(self, other):
        return self.__wrap_binary_op(other, op.mul, float)

    def __rmul__(self, other):
        return self.__wrap_binary_op(other, op.mul, float, True)

    def __truediv__(self, other):
        return self.__wrap_binary_op(other, op.truediv, float)

    def __rtruediv__(self, other):
        return self.__wrap_binary_op(other, op.truediv, float, True)

    def __call__(self, *args, **kwargs):
        return Condition.map(self, lambda f: f(*args, **kwargs))

    def __getattr__(self, name):
        """Priority: __getattr__ > __getitem__"""
        return Condition.map(self, get_attr_or_item(name))

    def __getitem__(self, item):
        """Priority: __getitem__ > __getattr__"""
        return Condition.map(self, get_item_or_attr(item))

    def __wrap_binary_op(self, other, op, coerce=lambda x: x, swap=False):
        other = Condition.wrap(other)
        return Condition.flatmap(
            self,
            lambda x: Condition.map(
                other,
                lambda y: (
                    op(coerce(y), coerce(x)) if swap else op(coerce(x), coerce(y))
                ),
            ),
        )

    def __bool__(self):
        raise Exception(
            """
            It is intentional that Condition objects should not be used as boolean values.

            If you're trying to use boolean operators with conditions, please use function equivalents instead:
              a and b -> and_(a, b)
              a or b -> or_(a, b)
              not a -> not_(a)

            If you're trying to use the `in` operator, please also use function equivalent instead:
              a in b -> has(b, a)
            """
        )


def get_attr_or_item(name):
    def __get_attr_or_item(x):
        try:
            if hasattr(x, name):
                return getattr(x, name)
            if hasattr(x, "__getitem__"):
                return x[name]
        except (KeyError, IndexError, TypeError):
            return None
        return None

    return __get_attr_or_item


def get_item_or_attr(item):
    def __get_item_or_attr(x):
        try:
            if hasattr(x, "__getitem__"):
                return x[item]
            if hasattr(x, item):
                return getattr(x, item)
        except (KeyError, IndexError, TypeError):
            return None
        return None

    return __get_item_or_attr


class ThunkCondition(Condition):
    def __init__(self, thunk):
        super().__init__()
        self.__thunk = thunk

    def evaluate_condition_at(self, item, scope):
        return self.__thunk(item, scope)


class MappedCondition(Condition):
    def __init__(self, inner, mapper):
        super().__init__()
        self.__inner = inner
        self.__mapper = mapper

    def evaluate_condition_at(self, item, scope):
        value, scope = self.__inner.evaluate_condition_at(item, scope)
        if value is not None:
            value = self.__mapper(value)

        return value, scope


__all__ = [
    "Condition",
    "ThunkCondition",
]
