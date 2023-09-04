import unittest
from collections import namedtuple

from ruleengine.dsl.action import Action
from ruleengine.dsl.base_conditions import *
from ruleengine.engine import Engine, Rule

MockDataItem = namedtuple("MockDataItem", "topic msg ts msgtype")
MockMessage = namedtuple("MockMessage", "int_value str_value")

simple_sequence = [
    MockDataItem("t1", MockMessage(1, "hello"), 0, "MockMessage"),
    MockDataItem("t2", MockMessage(2, "hello"), 1, "MockMessage"),
    MockDataItem("t1", MockMessage(3, "heLlo"), 2, "MockMessage"),
    MockDataItem("t2", MockMessage(4, "hello"), 3, "MockMessage"),
    MockDataItem("t2", MockMessage(5, "world"), 4, "MockMessage"),
    MockDataItem(
        "t3",
        MockMessage(5, "The value is 324, which is expected to be less than 22"),
        5,
        "MockMessage",
    ),
    MockDataItem(
        "t3",
        MockMessage(5, "The value is 11, which is expected to be less than 22"),
        5,
        "MockMessage",
    ),
]


class CollectAction(Action):
    def __init__(self):
        self.collector = []

    def run(self, item, scope):
        self.collector.append(item)


class BaseConditionTest(unittest.TestCase):
    def test_always(self):
        result = self.__run_test(always)
        self.assertEqual(len(result), 7, result)

    def test_identity(self):
        result = self.__run_test(
            identity == MockDataItem("t1", MockMessage(1, "hello"), 0, "MockMessage")
        )
        self.assertEqual(len(result), 1, result)

    def test_msg(self):
        result = self.__run_test(msg == MockMessage(1, "hello"))
        self.assertEqual(len(result), 1, result)

    def test_ts(self):
        result = self.__run_test(ts == 0)
        self.assertEqual(len(result), 1, result)

    def test_topic(self):
        result = self.__run_test(topic == "t1")
        self.assertEqual(len(result), 2, result)

    def test_msgtype(self):
        result = self.__run_test(msgtype == "MockMessage")
        self.assertEqual(len(result), 7, result)

        result = self.__run_test(msgtype == "FalseMessage")
        self.assertEqual(len(result), 0, result)

    def test_none_values(self):
        result = self.__run_test(msg.this.doesnt.exist == "MockMessage")
        self.assertEqual(len(result), 0, result)

        result = self.__run_test(is_none(msg.this.doesnt.exist))
        self.assertEqual(len(result), 7, result)

    def test_and(self):
        result = self.__run_test(and_(msgtype == "MockMessage", topic == "t1"))
        self.assertEqual(len(result), 2, result)

    def test_or(self):
        result = self.__run_test(or_(ts == 1, topic == "t1"))
        self.assertEqual(len(result), 3, result)

    def test_not(self):
        result = self.__run_test(not_(ts == 1))
        self.assertEqual(len(result), 6, result)

    def test_topic_match(self):
        result = self.__run_test(topic_is("t1"))
        self.assertEqual(len(result), 2, result)

    def test_type_match(self):
        result = self.__run_test(type_is("MockMessage"))
        self.assertEqual(len(result), 7, result)

        result = self.__run_test(type_is("FalseMessage"))
        self.assertEqual(len(result), 0, result)

    def test_complex_conditions(self):
        result = self.__run_test(and_(topic_is("t2"), msg.int_value > 2))
        self.assertEqual(len(result), 2, result)

    def test_function_calls(self):
        result = self.__run_test(msg.str_value.upper() == "HELLO")
        self.assertEqual(len(result), 4, result)

    def test_get_set_values(self):
        result = self.__run_test(
            and_(set_value("somekey", msg.str_value), get_value("somekey") == "hello")
        )
        self.assertEqual(len(result), 3, result)

    def test_has(self):
        result = self.__run_test(
            and_(has(msg.str_value, "el"), get_value("cos/contains") == "el")
        )
        self.assertEqual(len(result), 3, result)
        result = self.__run_test(
            and_(has(msg.str_value, "el"), get_value("cos/contains") == "ee")
        )
        self.assertEqual(len(result), 0, result)

    def test_regex(self):
        result = self.__run_test(
            regex_search(msg.str_value, r"e[lL]lo").group(0) == "ello",
        )
        self.assertEqual(len(result), 3, result)
        result = self.__run_test(
            regex_search(msg.str_value, r"e[lL]lo").group(0) == "eLlo",
        )
        self.assertEqual(len(result), 1, result)

    def test_concat(self):
        result = self.__run_test(
            concat(msg.str_value, "---", msg.int_value) == "hello---1"
        )
        self.assertEqual(len(result), 1, result)

    def test_coerce(self):
        result = self.__run_test(
            regex_search(
                msg.str_value,
                r"The value is (\d+), which is expected to be less than",
            ).group(1)
            > 111,
        )
        self.assertEqual(len(result), 1, result)

    @staticmethod
    def __run_test(condition):
        action = CollectAction()
        Engine([Rule(condition, action)], simple_sequence).run()
        return action.collector
