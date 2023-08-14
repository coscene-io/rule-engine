import operator as op
from abc import ABC, abstractmethod


class Condition(ABC):
    """
    Defines a condition to be evaluated on a single message.

    It is assumed that the message has three fields, mirroring those of the ROS
    bag reader API:

    - topic
    - msg
    - ts

    To make the DSL look nice at the end, this class ends up taking on a lot of
    the complexity. If you're familiar with monads, this class is a combination
    of Future and State. `map_condition_value` is both map and flatmap, and
    `wrap` is lift.

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
            mapped = mapper(value1)
            if not isinstance(mapped, Condition):
                return mapped, scope

            return mapped.evaluate_condition_at(item, scope)

        return ThunkCondition(new_thunk)

    def __and__(self, other):
        # We don't implement `and` using the usual __wrap_binary_op, because we
        # need to short circuit if the first value returns false. Same for `or`
        def new_thunk(item, scope):
            value1, scope = self.evaluate_condition_at(item, scope)
            if not value1:
                return value1, scope
            return Condition.wrap(other).evaluate_condition_at(item, scope)

        return ThunkCondition(new_thunk)

    def __or__(self, other):
        def new_thunk(item, scope):
            value1, scope = self.evaluate_condition_at(item, scope)
            if value1:
                return value1, scope
            return Condition.wrap(other).evaluate_condition_at(item, scope)

        return ThunkCondition(new_thunk)

    def __invert__(self):
        return self.map_condition_value(op.not_)

    def __rshift__(self, other):
        # Python won't let us override `a in b` properly, so we repurpose b >> a
        # to mean "b contains a".
        return self.__wrap_binary_op(other, op.contains)

    def __eq__(self, other):
        return self.__wrap_binary_op(other, op.eq)

    def __ne__(self, other):
        return self.__wrap_binary_op(other, op.ne)

    def __gt__(self, other):
        return self.__wrap_binary_op(other, op.gt)

    def __ge__(self, other):
        return self.__wrap_binary_op(other, op.ge)

    def __lt__(self, other):
        return self.__wrap_binary_op(other, op.lt)

    def __le__(self, other):
        return self.__wrap_binary_op(other, op.le)

    def __call__(self, *args, **kwargs):
        return self.map_condition_value(lambda f: f(*args, **kwargs))

    def __getattr__(self, name):
        return self.map_condition_value(lambda x: getattr(x, name))

    def __wrap_binary_op(self, other, op):
        return self.map_condition_value(
            lambda x: Condition.wrap(other).map_condition_value(
                lambda y: op(x, y)))

    def __bool__(self):
        pass
        raise NotImplementedError("""
        It is intentional that Condition objects should not be used as boolean values.

        If you're trying to use boolean operators with conditions, please use bitwise equivalents instead:
          a and b -> a & b
          a or b -> a | b
          not a -> ~a

        If you're trying to use the `in` operator, we've repurposed bitshift operators for that:
          a in b -> b >> a

        """)


class ThunkCondition(Condition):
    def __init__(self, thunk):
        super().__init__()
        self.__thunk = thunk

    def evaluate_condition_at(self, item, scope):
        return self.__thunk(item, scope)
