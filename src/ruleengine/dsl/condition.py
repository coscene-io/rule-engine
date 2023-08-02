from abc import ABC, abstractmethod
import operator as op

class Condition(ABC):
    @abstractmethod
    def evaluate_condition_at(self, item):
        pass

class PointCondition(Condition):
    def __init__(self, thunk=lambda item, scope: (item, scope)):
        super().__init__()
        self.__thunk = thunk

    def evaluate_condition_at(self, item, scope):
        return self.__thunk(item, scope)

    def map_condition_value(self, mapper):
        def new_thunk(item, scope):
            value_1, scope_1 = self.__thunk(item, scope)
            mapped = mapper(value_1)
            if isinstance(mapped, PointCondition):
                value_2, scope_2 = value.evaluate_condition_at(item, scope_1)
                return value_2, { **scope_1, **scope_2 }
            return mapped, scope_1
        return PointCondition(new_thunk)

    def __and__(self, other):
        return self.__wrap_binary_op(other, op.and_)

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
        if isinstance(other, PointCondition):
            return self.map_condition_value(
                lambda x: other.map_condition_value(
                    lambda y: op(x, y)))
        return self.map_condition_value(lambda x: op(x, other))


