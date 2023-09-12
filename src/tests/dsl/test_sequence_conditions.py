import unittest
from collections import namedtuple

from ruleengine.dsl.action import Action
from ruleengine.dsl.base_conditions import *
from ruleengine.dsl.sequence_conditions import *
from ruleengine.engine import Engine

MockDataItem = namedtuple("MockDataItem", "topic msg ts")
MockMessage = namedtuple("MockMessage", "int_value str_value")

simple_sequence = [
    MockDataItem("t1", MockMessage(1, "1111"), 0),
    MockDataItem("t1", MockMessage(2, "aaaa"), 1),
    MockDataItem("t2", MockMessage(1, "aaaa"), 2),
    MockDataItem("t2", MockMessage(2, "aaaa"), 3),
    MockDataItem("t1", MockMessage(3, "2222"), 4),
    MockDataItem("t1", MockMessage(3, "1111"), 5),
    MockDataItem("t2", MockMessage(4, "aaaa"), 6),
    MockDataItem("t2", MockMessage(4, "aaaa"), 7),
    MockDataItem("t1", MockMessage(1, "aaaa"), 8),
    MockDataItem("t1", MockMessage(2, "4444"), 9),
    MockDataItem("t2", MockMessage(1, "aaaa"), 10),
    MockDataItem("t2", MockMessage(2, "aaaa"), 11),
    MockDataItem("t1", MockMessage(3, "3333"), 12),
    MockDataItem("t1", MockMessage(3, "aaaa"), 13),
    MockDataItem("t2", MockMessage(4, "aaaa"), 14),
    MockDataItem("t2", MockMessage(4, "3333"), 15),
    MockDataItem("t1", MockMessage(1, "4444"), 16),
    MockDataItem("t1", MockMessage(2, "2222"), 17),
    MockDataItem("t2", MockMessage(1, "aaaa"), 18),
    MockDataItem("t2", MockMessage(2, "aaaa"), 19),
    MockDataItem("t1", MockMessage(3, "aaaa"), 20),
    MockDataItem("t1", MockMessage(3, "aaaa"), 21),
    MockDataItem("t2", MockMessage(4, "aaaa"), 22),
    MockDataItem("t2", MockMessage(4, "5555"), 23),
]


class CollectAction(Action):
    def __init__(self):
        self.collector = []

    def run(self, item, scope):
        self.collector.append((item, scope))


def get_start_times(res):
    return [i[1]["start_time"] for i in res]


def get_trigger_times(res):
    return [i[0].ts for i in res]


class SequenceConditionTest(unittest.TestCase):
    def test_sustained_sequence(self):
        result = self.__run_test(sustained(always, msg.str_value == "hello", 2))
        self.assertEqual(get_start_times(result), [0, 5])

        result = self.__run_test(sustained(always, msg.str_value == "hello", 6))
        self.assertEqual(get_start_times(result), [])

        result = self.__run_test(sustained(topic == "t1", msg.str_value == "hello", 2))
        self.assertEqual(get_start_times(result), [0])

        result = self.__run_test(sustained(topic == "t1", msg.str_value == "hello", 6))
        self.assertEqual(get_start_times(result), [])

    def test_sequence_pattern(self):
        result = self.__run_test(
            sequential(
                and_(topic == "t1", msg.int_value == 1),
                and_(
                    topic == "t2",
                    (msg.int_value == 4),
                    set_value("somekey", msg.int_value),
                ),
                and_(topic == "t2", msg.int_value == get_value("somekey")),
                duration=4,
            )
        )
        self.assertEqual(get_start_times(result), [0])

        result = self.__run_test(
            sequential(
                and_(topic == "t1", msg.int_value == 1),
                and_(
                    topic == "t2",
                    (msg.int_value == 4),
                    set_value("somekey", msg.int_value),
                ),
                and_(topic == "t2", msg.int_value == get_value("somekey")),
                duration=2,
            )
        )
        self.assertEqual(get_start_times(result), [])

        # Overlapping sequences, and without duration
        result = self.__run_test(
            sequential(
                and_(topic == "t1", set_value("somekey", msg.int_value)),
                and_(topic == "t2", msg.int_value == get_value("somekey")),
            )
        )
        self.assertEqual(get_start_times(result), [0, 0])

    def test_sequence_timeout(self):
        result = self.__run_test(
            timeout(has(msg.str_value, "1111"),
                    any_order(has(msg.str_value, "2222"), has(msg.str_value, "3333"), has(msg.str_value, "4444")),
                    duration=10)
        )
        self.assertEqual(get_start_times(result), [0, 5])

    def test_repeated(self):
        result = self.__run_test(repeated(always, 2, 5))
        self.assertEqual(get_start_times(result), [0])

        result = self.__run_test(repeated(topic == "t2", 2, 5))
        self.assertEqual(get_start_times(result), [1])

        result = self.__run_test(repeated(topic == "t2", 5, 5))
        self.assertEqual(get_start_times(result), [1])

        result = self.__run_test(repeated(topic == "t2", 2, 0.5))
        self.assertEqual(get_start_times(result), [1, 3, 4, 7])

    def test_debounce(self):
        result = self.__run_test(debounce(msg.str_value == "hello", 3))
        self.assertEqual(get_trigger_times(result), [0])

        result = self.__run_test(debounce(msg.str_value == "hello", 1.5))
        self.assertEqual(get_trigger_times(result), [0, 5, 9])

        result = self.__run_test(debounce(msg.str_value == "single", 3))
        self.assertEqual(get_trigger_times(result), [9])

    def test_throttle(self):
        result = self.__run_test(throttle(msg.str_value == "hello", 3))
        self.assertEqual(get_trigger_times(result), [0, 3, 6, 9])

    def test_any_order(self):
        result = self.__run_test(any_order(topic == "t1", topic == "t2", topic == "t3"))
        self.assertEqual(get_trigger_times(result), [9])

        result = self.__run_test(any_order(topic == "t3", topic == "t2", topic == "t1"))
        self.assertEqual(get_trigger_times(result), [9])

    @staticmethod
    def __run_test(condition):
        action = CollectAction()
        engine = Engine([([condition], [action])])
        for item in simple_sequence:
            engine.consume_next(item)
        return action.collector
