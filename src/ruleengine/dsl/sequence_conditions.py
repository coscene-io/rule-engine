from .condition import PointCondition, Condition

def sustained(context_condition, variable_condition, duration):
    """
    This condition triggers when the variable condition continues to be true for
    the given duration.

    The context condition is used to limit the scope of the variable condition.
    For example, we might say "if topic X has value Y for 10 seconds", which
    translates to context being topic == X, and variable being value == Y
    """
    return FilterCondition(context_condition, SustainedCondition(variable_condition, duration))


class SustainedCondition(Condition):
    def __init__(self, variable_condition, duration):
        assert isinstance(variable_condition, PointCondition)

        self.__variable = variable_condition
        self.__duration = duration
        self.__start = None
        self.__active = False

    def evaluate_condition_at(self, item, scope):
        value, scope_update = self.__variable.evaluate_condition_at(item, scope)
        if not value:
            self.__start = None
            self.__active = False
            return False, scope_update

        if self.__active:
            return False, scope_update

        if self.__start is None:
            self.__start = item.ts

        if item.ts - self.__start > self.__duration:
            self.__active = True
            return True, { **scope_update, 'start_time': self.__start }

        return False, scope_update


class FilterCondition(Condition):
    def __init__(self, filter_condition, child_condition):
        assert isinstance(filter_condition, PointCondition)
        assert isinstance(child_condition, Condition)

        self.__filter = filter_condition
        self.__child = child_condition

    def evaluate_condition_at(self, item, scope):
        value, scope_update = self.__filter.evaluate_condition_at(item, scope)
        if not value:
            return False, scope_update

        value2, update2 = self.__child.evaluate_condition_at(item, scope | scope_update)
        return value2, scope_update | update2

