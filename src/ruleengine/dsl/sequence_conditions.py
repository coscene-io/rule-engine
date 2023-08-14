from .base_conditions import and_
from .condition import Condition


def sustained(context_condition, variable_condition, duration):
    """
    This condition triggers when the variable condition continues to be true for
    the given duration.

    The context condition is used to limit the scope of the variable condition.
    For example, we might say "if topic X has value Y for 10 seconds", which
    translates to context being topic == X, and variable being value == Y
    """
    return and_(context_condition, SustainedCondition(variable_condition, duration))


def sequential(*conditions, duration=None):
    return SequenceMatchCondition(list(conditions), duration)


def repeated(condition, times, duration):
    return and_(condition, SustainedCondition(SequenceMatchCondition([condition] * times, duration)))


def debounce(condition, duration):
    return repeated(condition, 2, duration)


class SustainedCondition(Condition):
    def __init__(self, variable_condition, duration=-1):
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
            return True, {**new_scope, 'start_time': self.__start}

        return False, new_scope


class SequenceMatchCondition(Condition):
    def __init__(self, sequence, duration=None):
        super().__init__()

        assert len(sequence) > 1, 'Sequence must be longer than 1'
        for c in sequence:
            assert isinstance(c, Condition)

        self.__seq = sequence
        self.__duration = duration

        # List of (start time, current index, scope) tuple. Each item denotes
        # one ongoing matching sequence, with start time being the time of the
        # first matched condition, and current index is the next condition to be
        # matched
        self.__ongoings = []

    def evaluate_condition_at(self, item, scope):
        ongoings = []
        success = None
        for start, curr_index, curr_scope in self.__ongoings:
            if self.__duration is not None and item.ts - start > self.__duration:
                continue

            matched, new_scope = self.__seq[curr_index].evaluate_condition_at(item, curr_scope)
            if matched:
                if curr_index + 1 == len(self.__seq):
                    success = start, new_scope
                else:
                    ongoings.append((start, curr_index + 1, new_scope))

            else:
                ongoings.append((start, curr_index, curr_scope))

        self.__ongoings = ongoings

        matched, new_scope = self.__seq[0].evaluate_condition_at(item, scope)
        if matched:
            self.__ongoings.append((item.ts, 1, new_scope))

        if success:
            return True, {**success[1], 'start_time': success[0]}

        return False, scope
