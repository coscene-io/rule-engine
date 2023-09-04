import unittest
from collections import namedtuple

from ruleengine.dsl.action import Action
from ruleengine.dsl.base_conditions import *
from ruleengine.dsl.log_conditions import *
from ruleengine.engine import Engine, Rule

MockDataItem = namedtuple("MockDataItem", "topic msg ts msgtype")
MockMessage = namedtuple("MockMessage", "int_value str_value")
RosMockMessage = namedtuple("RosMockMessage", "msg level")
FoxgloveMockMessage = namedtuple("FoxgloveMockMessage", "message level")

simple_sequence = [
    MockDataItem("t1", MockMessage(1, "hello"), 0, "MockMessage"),
    MockDataItem("t2", MockMessage(2, "hello"), 1, "MockMessage"),
    MockDataItem("t1", RosMockMessage("ros log message 1", 3), 2, "rosgraph_msgs/Log"),
    MockDataItem("t1", RosMockMessage("ros log message 1", 4), 3, "rosgraph_msgs/Log"),
    MockDataItem("t1", RosMockMessage("ros log message 1", 7), 4, "MockMessage"),
    MockDataItem(
        "t2", FoxgloveMockMessage("foxglove log message 1", 2), 5, "foxglove_msgs/Log"
    ),
    MockDataItem(
        "t2", FoxgloveMockMessage("foxglove log message 2", 3), 6, "foxglove.Log"
    ),
    MockDataItem(
        "t2", FoxgloveMockMessage("foxglove log message 2", 7), 7, "foxglove.Log"
    ),
]


class CollectAction(Action):
    def __init__(self):
        self.collector = []

    def run(self, item, scope):
        self.collector.append(item)


class LogConditionTest(unittest.TestCase):
    def test_log_test(self):
        result = self.__run_test(log_text != "")
        self.assertEqual(len(result), 5, result)

        result = self.__run_test(log_text == "ros log message 1")
        self.assertEqual(len(result), 2, result)

        result = self.__run_test(has(log_text, "foxglove log message"))
        self.assertEqual(len(result), 3, result)

    def test_log_level(self):
        result = self.__run_test(log_level == LogLevel.DEBUG)
        self.assertEqual(len(result), 0, result)

        result = self.__run_test(log_level == LogLevel.INFO)
        self.assertEqual(len(result), 1, result)

        result = self.__run_test(log_level == LogLevel.WARN)
        self.assertEqual(len(result), 2, result)

        result = self.__run_test(log_level == LogLevel.UNKNOWN)
        self.assertEqual(len(result), 5, result)

    @staticmethod
    def __run_test(condition):
        action = CollectAction()
        Engine([Rule(condition, action)], simple_sequence).run()
        return action.collector
