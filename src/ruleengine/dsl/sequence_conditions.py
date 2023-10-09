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


def sequential(*condition_factories, duration=None):
    return SequenceMatchCondition(list(condition_factories), duration)


def timeout(*condition_factories, duration):
    return SequenceMatchCondition(list(condition_factories), duration, True)


def any_order(*conditions):
    return RisingEdgeCondition(AnyOrderCondition(list(conditions)))


def repeated(condition_factory, /, times, duration):
    assert times > 1, "In repeated condition, times must be more than 1"
    return and_(
        condition_factory(),
        RisingEdgeCondition(
            SequenceMatchCondition([condition_factory] * times, duration)
        ),
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
    """
    This condition triggers when the child condition is true for the given
    duration.
    The state is reset once the child condition becomes false.
    """

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
    """
    This condition triggers when the child conditions are true in the given
    order, and within the given duration if set.

    If trigger_on_timeout is set, the condition will only trigger when the
    sequence is not matched within the given duration.

    Note that the sequence input is a list of condition factories, not conditions.
    """

    def __init__(self, factory_sequence, duration=None, trigger_on_timeout=False):
        super().__init__()

        assert len(factory_sequence) > 1, "Sequence must be longer than 1"
        for factory in factory_sequence:
            assert isinstance(factory(), Condition)

        self.__factory_seq = factory_sequence
        self.__duration = duration
        self.__trigger_on_timeout = trigger_on_timeout

        # List of (start time, current index, scope, seq) tuple. Each item denotes
        # one ongoing matching sequence, with start time being the time of the
        # first matched condition, and current index is the next condition to be
        # matched
        self.__ongoings = []

    def generate_sequence(self):
        return [factory() for factory in self.__factory_seq]

    def evaluate_condition_at(self, item, scope):
        ongoings = []
        success = None
        for start, curr_index, curr_scope, seq in self.__ongoings:
            if self.__duration is not None and item.ts - start > self.__duration:
                if self.__trigger_on_timeout:
                    success = start, curr_scope
                continue

            matched, new_scope = seq[curr_index].evaluate_condition_at(item, curr_scope)
            if matched:
                if curr_index + 1 == len(seq):
                    if not self.__trigger_on_timeout:
                        success = start, new_scope
                else:
                    ongoings.append((start, curr_index + 1, new_scope, seq))

            else:
                ongoings.append((start, curr_index, curr_scope, seq))

        self.__ongoings = ongoings

        seq = self.generate_sequence()
        matched, new_scope = seq[0].evaluate_condition_at(item, scope)
        if matched:
            self.__ongoings.append((item.ts, 1, new_scope, seq))

        if success:
            return True, {**success[1], "start_time": success[0]}

        return False, scope


class ThrottleCondition(Condition):
    """
    This condition triggers when the child condition is true, but only if the
    last trigger is more than the given duration ago.
    """

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


class AnyOrderCondition(Condition):
    """
    This condition triggers when all the child conditions are true, but the
    order of the conditions does not matter.
    The condition will remain true once triggered.
    """

    def __init__(self, conditions):
        self.__unsatisfied = conditions
        self.__curr_scope = None

    def evaluate_condition_at(self, item, scope):
        if self.__curr_scope is None:
            self.__curr_scope = scope

        new_conditions = []
        for c in self.__unsatisfied:
            value, new_scope = c.evaluate_condition_at(item, self.__curr_scope)
            if value:
                self.__curr_scope = new_scope
            else:
                new_conditions.append(c)

        if not new_conditions:
            return True, self.__curr_scope

        self.__unsatisfied = new_conditions
        return False, self.__curr_scope


__all__ = [
    "any_order",
    "debounce",
    "repeated",
    "sequential",
    "sustained",
    "throttle",
    "timeout",
]
