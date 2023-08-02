from abc import ABC, abstractmethod
import operator as op

class Condition(ABC):
    @abstractmethod
    def evaluate_condition_at(self, item, scope):
        pass


class PointCondition(Condition):
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
    def __init__(self, thunk=lambda item, scope: item):
        super().__init__()
        self.__thunk = thunk

    @staticmethod
    def wrap(value):
        if isinstance(value, PointCondition):
            return value
        return PointCondition(lambda item, scope: value)

    def evaluate_condition_at(self, item, scope):
        return self.__thunk(item, scope)

    def map_condition_value(self, mapper):
        def new_thunk(item, scope):
            mapped = mapper(self.evaluate_condition_at(item, scope))
            if isinstance(mapped, PointCondition):
                return mapped.evaluate_condition_at(item, scope)
            return mapped
        return PointCondition(new_thunk)

    def __and__(self, other):
        def new_thunk(item, scope):
             new_value = self.evaluate_condition_at(item, scope)
             if not new_value:
                 return new_value
             return PointCondition.wrap(other).evaluate_condition_at(item, scope)

        return PointCondition(new_thunk)

    def __contains__(self, other):
        return self.__wrap_binary_op(other, op.contains)

    def __eq__(self, other):
        return self.__wrap_binary_op(other, op.eq)

    def __gt__(self, other):
        return self.__wrap_binary_op(other, op.gt)

    def __call__(self, *args, **kwargs):
        return self.map_condition_value(lambda f: f(*args, **kwargs))

    def __getattr__(self, name):
        return self.map_condition_value(lambda x: getattr(x, name))

    def __wrap_binary_op(self, other, op):
        return self.map_condition_value(
            lambda x: PointCondition.wrap(other).map_condition_value(
                lambda y: op(x, y)))

