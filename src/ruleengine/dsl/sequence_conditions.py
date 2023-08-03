from .ruleengine.dsl.condition import PointCondition, Condition

def sustained(context_condition, variable_condition, duration):
    return FilterCondition(context_condition, SustainedCondition(variable_condition, duration))


class SustainedCondition(Condition):
    def __init__(self, variable_condition, duration):
        assert isinstance(variable_condition, PointCondition)

        self.__variable = variable_condition
        self.__duration = duration
        self.__start = None
        self.__active = False

    def evaluate_condition_at(self, item, scope):
        if not self.__variable.evaluate_condition_at(item, scope):
            self.__start = None
            self.__active = False
            return False

        if self.__active:
            return False

        if self.__start is None:
            self.__start = item.ts

        if item.ts - self.__start > duration:
            scope['start_time'] = self.__start
            self.__active = True
            return True


class FilterCondition(Condition):
    def __init__(self, filter_condition, child_condition):
        assert isinstance(filter_condition, PointCondition)
        assert isinstance(child_condition, Condition)

        self.__filter = filter_condition
        self.__child = child_condition

    def evaluate_condition_at(self, item, scope):
        if not self.__filter.evaluate_condition_at(item, scope):
            return False

        return self.__child.evaluate_condition_at(item, scope)
