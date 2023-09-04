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
    return and_(
        context_condition,
        RisingEdgeCondition(SustainedCondition(variable_condition, duration)),
    )


def sequential(*conditions, duration=None):
    return SequenceMatchCondition(list(conditions), duration)


def repeated(condition, times, duration):
    return and_(
        condition,
        RisingEdgeCondition(SequenceMatchCondition([condition] * times, duration)),
    )


def debounce(condition, duration):
    return and_(condition, RisingEdgeCondition(condition, duration))


def throttle(condition, duration):
    return ThrottleCondition(condition, duration)


class RisingEdgeCondition(Condition):
    """
    A condition that detects when child condition changes from false to true.

    Once child condition becomes true, this condition will not fire unless the
    child condition first becomes false, then back to true.

    If max_gap is given, and two invocations of this condition have timestamps
    further apart than the gap, the state is reset. It behaves as if a false is
    inserted in the gap.
    """

    def __init__(self, condition, max_gap=None):
        assert isinstance(condition, Condition)
        self.__condition = condition
        self.__active = False
        self.__last_activation = None
        self.__max_gap = max_gap

    def evaluate_condition_at(self, item, scope):
        value, new_scope = self.__condition.evaluate_condition_at(item, scope)
        if not value:
            self.__active = False
            return False, new_scope

        if self.__active and (
            self.__max_gap is None or item.ts - self.__last_activation < self.__max_gap
        ):
            self.__last_activation = item.ts
            return False, new_scope

        self.__active = True
        self.__last_activation = item.ts
        return True, new_scope


class SustainedCondition(Condition):
    def __init__(self, condition, duration=-1):
        super().__init__()

        assert isinstance(condition, Condition)
        self.__condition = condition
        self.__duration = duration
        self.__start = None

    def evaluate_condition_at(self, item, scope):
        value, new_scope = self.__condition.evaluate_condition_at(item, scope)
        if not value:
            self.__start = None
            return False, new_scope

        if self.__start is None:
            self.__start = item.ts

        if item.ts - self.__start > self.__duration:
            return True, {**new_scope, "start_time": self.__start}

        return False, new_scope


class SequenceMatchCondition(Condition):
    def __init__(self, sequence, duration=None):
        super().__init__()

        assert len(sequence) > 1, "Sequence must be longer than 1"
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

            matched, new_scope = self.__seq[curr_index].evaluate_condition_at(
                item, curr_scope
            )
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
            return True, {**success[1], "start_time": success[0]}

        return False, scope


class ThrottleCondition(Condition):
    def __init__(self, condition, duration):
        assert isinstance(condition, Condition)
        self.__condition = condition
        self.__duration = duration
        self.__last_trigger = -duration

    def evaluate_condition_at(self, item, scope):
        if item.ts - self.__last_trigger < self.__duration:
            return False, scope

        value, scope = self.__condition.evaluate_condition_at(item, scope)
        if value:
            self.__last_trigger = item.ts
            return value, scope

        return False, scope


__all__ = [
    "sustained",
    "sequential",
    "repeated",
    "debounce",
    "throttle",
]
