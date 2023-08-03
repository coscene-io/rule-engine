from .condition import Condition

def sustained(context_condition, variable_condition, duration):
    """
    This condition triggers when the variable condition continues to be true for
    the given duration.

    The context condition is used to limit the scope of the variable condition.
    For example, we might say "if topic X has value Y for 10 seconds", which
    translates to context being topic == X, and variable being value == Y
    """
    return context_condition & SustainedCondition(variable_condition, duration)


class SustainedCondition(Condition):
    def __init__(self, variable_condition, duration):
        super().__init__()
        assert isinstance(variable_condition, Condition)

        self.__variable = variable_condition
        self.__duration = duration
        self.__start = None
        self.__active = False

    def evaluate_condition_at(self, item, scope):
        value, new_scope = self.__variable.evaluate_condition_at(item, scope)
        if not value:
            self.__start = None
            self.__active = False
            return False, new_scope

        if self.__active:
            return False, new_scope

        if self.__start is None:
            self.__start = item.ts

        if item.ts - self.__start > self.__duration:
            self.__active = True
            return True, { **new_scope, 'start_time': self.__start }

        return False, new_scope


