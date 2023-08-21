import unittest
from collections import namedtuple

from ruleengine.dsl.actions import Action
from ruleengine.dsl.base_conditions import *
from ruleengine.dsl.sequence_conditions import repeated, sequential, sustained
from ruleengine.engine import Engine, Rule

MockDataItem = namedtuple("MockDataItem", "topic msg ts")
MockMessage = namedtuple("MockMessage", "int_value str_value")

simple_sequence = [
    MockDataItem("t1", MockMessage(1, "hello"), 0),
    MockDataItem("t1", MockMessage(2, "hello"), 0),
    MockDataItem("t2", MockMessage(1, "hello"), 1),
    MockDataItem("t2", MockMessage(2, "hello"), 1),
    MockDataItem("t1", MockMessage(3, "hello"), 2),
    MockDataItem("t1", MockMessage(3, "hello"), 3),
    MockDataItem("t2", MockMessage(4, "hello"), 3),
    MockDataItem("t2", MockMessage(4, "hello"), 3),
    MockDataItem("t2", MockMessage(5, "world"), 4),
    MockDataItem("t2", MockMessage(5, "world"), 4),
    MockDataItem("t2", MockMessage(4, "hello"), 5),
    MockDataItem("t2", MockMessage(4, "hello"), 6),
    MockDataItem("t2", MockMessage(4, "hello"), 7),
    MockDataItem("t2", MockMessage(4, "hello"), 7),
    MockDataItem("t2", MockMessage(4, "hello"), 9),
]


class CollectAction(Action):
    def __init__(self):
        self.collector = []

    def run(self, item, scope):
        self.collector.append((item, scope))


def get_start_times(res):
    return [i[1]["start_time"] for i in res]


class SequenceConditionTest(unittest.TestCase):
    def test_sustained_sequence(self):
        result = self.__run_test(sustained(always, msg.str_value == "hello", 2))
        self.assertEqual(get_start_times(result), [0, 5])

        result = self.__run_test(sustained(always, msg.str_value == "hello", 6))
        self.assertEqual(get_start_times(result), [])

        result = self.__run_test(sustained(topic_is("t1"), msg.str_value == "hello", 2))
        self.assertEqual(get_start_times(result), [0])

        result = self.__run_test(sustained(topic_is("t1"), msg.str_value == "hello", 6))
        self.assertEqual(get_start_times(result), [])

    def test_sequence_pattern(self):
        result = self.__run_test(
            sequential(
                and_(topic_is("t1"), msg.int_value == 1),
                and_(
                    topic_is("t2"),
                    (msg.int_value == 4),
                    set_value("somekey", msg.int_value),
                ),
                and_(topic_is("t2"), msg.int_value == get_value("somekey")),
                duration=4,
            )
        )
        self.assertEqual(get_start_times(result), [0])

        result = self.__run_test(
            sequential(
                and_(topic_is("t1"), msg.int_value == 1),
                and_(
                    topic_is("t2"),
                    (msg.int_value == 4),
                    set_value("somekey", msg.int_value),
                ),
                and_(topic_is("t2"), msg.int_value == get_value("somekey")),
                duration=2,
            )
        )
        self.assertEqual(get_start_times(result), [])

        # Overlapping sequences, and without duration
        result = self.__run_test(
            sequential(
                and_(topic_is("t1"), set_value("somekey", msg.int_value)),
                and_(topic_is("t2"), msg.int_value == get_value("somekey")),
            )
        )
        self.assertEqual(get_start_times(result), [0, 0])

    def test_repeated(self):
        result = self.__run_test(repeated(always, 2, 5))
        self.assertEqual(get_start_times(result), [0])

        result = self.__run_test(repeated(topic_is("t2"), 2, 5))
        self.assertEqual(get_start_times(result), [1])

        result = self.__run_test(repeated(topic_is("t2"), 5, 5))
        self.assertEqual(get_start_times(result), [4])

        result = self.__run_test(repeated(topic_is("t2"), 2, 0.5))
        self.assertEqual(get_start_times(result), [1, 3, 4, 7])

    @staticmethod
    def __run_test(condition):
        action = CollectAction()
        Engine([Rule(condition, action)], simple_sequence).run()
        return action.collector
