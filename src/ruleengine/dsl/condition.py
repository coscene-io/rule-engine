from abc import ABC, abstractmethod
import operator as op

class Condition(ABC):
    @abstractmethod
    def evaluate_condition_at(self, item):
        pass

class PointCondition(Condition):
    def __init__(self, thunk):
        super().__init__()
        self.__thunk = thunk

    def evaluate_condition_at(self, item):
        return self.__thunk(item)

    def map_condition_value(self, mapper):
        def new_thunk(item):
            value = mapper(self.__thunk(item))
            if isinstance(value, PointCondition):
                return value.evaluate_condition_at(item)
            return value
        return PointCondition(new_thunk)

    def __and__(self, other):
        return self.__wrap_binary_op(other, op.and_)

    def __contains__(self, other):
        return self.__wrap_binary_op(other, op.contains)

    def __getattr__(self, name):
        return self.map_condition_value(lambda x: getattr(x, name))

    def __wrap_binary_op(self, other, op):
        if isinstance(other, PointCondition):
            return self.map_condition_value(
                lambda x: other.map_condition_value(
                    lambda y: op(x, y)))
        return self.map_condition_value(lambda x: op(x, other))


