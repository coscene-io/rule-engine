import operator as op
from abc import ABC, abstractmethod


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
    of Future and State and Optional. `map_condition_value` is both map and
    flatmap, and `wrap` is pure.

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

    def map_condition_value(self, mapper):
        def new_thunk(item, scope):
            value1, scope = self.evaluate_condition_at(item, scope)
            if value1 is None:
                return value1, scope

            mapped = mapper(value1)
            if not isinstance(mapped, Condition):
                return mapped, scope

            return mapped.evaluate_condition_at(item, scope)

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
        return self.map_condition_value(op.neg)

    def __pos__(self):
        return self.map_condition_value(op.pos)

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
        return self.map_condition_value(lambda f: f(*args, **kwargs))

    def __getattr__(self, name):
        return self.map_condition_value(lambda x: getattr(x, name, None))

    def __wrap_binary_op(self, other, op, coerce=lambda x: x, swap=False):
        return self.map_condition_value(
            lambda x: Condition.wrap(other).map_condition_value(
                lambda y: op(coerce(y), coerce(x)) if swap else op(coerce(x), coerce(y))
            )
        )

    def __bool__(self):
        pass
        raise NotImplementedError(
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


class ThunkCondition(Condition):
    def __init__(self, thunk):
        super().__init__()
        self.__thunk = thunk

    def evaluate_condition_at(self, item, scope):
        return self.__thunk(item, scope)


__all__ = [
    "Condition",
    "ThunkCondition",
]
