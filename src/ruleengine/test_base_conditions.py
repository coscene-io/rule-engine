import unittest
from collections import namedtuple

from .dsl.actions import Action
from .dsl.base_conditions import and_, get_value, has, msg, regex_search, set_value, topic_is, type_is
from .engine import Engine, Rule

TestDataItem = namedtuple('TestDataItem', 'topic msg ts msgtype')
TestMessage = namedtuple('TestMessage', 'int_value str_value')

simple_sequence = [
    TestDataItem('t1', TestMessage(1, 'hello'), 0, 'TestMessage'),
    TestDataItem('t2', TestMessage(2, 'hello'), 1, 'TestMessage'),
    TestDataItem('t1', TestMessage(3, 'heLlo'), 2, 'TestMessage'),
    TestDataItem('t2', TestMessage(4, 'hello'), 3, 'TestMessage'),
    TestDataItem('t2', TestMessage(5, 'world'), 4, 'TestMessage'),
    TestDataItem('t3', TestMessage(5, 'The value is 324, which is expected to be less than 22'), 5, 'TestMessage'),
    TestDataItem('t3', TestMessage(5, 'The value is 11, which is expected to be less than 22'), 5, 'TestMessage'),
]


class TestAction(Action):
    def __init__(self):
        self.collector = []

    def run(self, item, scope):
        self.collector.append(item)


class BaseConditionTest(unittest.TestCase):
    def test_topic_match(self):
        result = self.__run_test(topic_is('t1'))
        self.assertEqual(len(result), 2, result)

    def test_type_match(self):
        result = self.__run_test(type_is('TestMessage'))
        self.assertEqual(len(result), 7, result)

    def test_complex_conditions(self):
        result = self.__run_test(and_(topic_is('t2'), msg.int_value > 2))
        self.assertEqual(len(result), 2, result)

    def test_function_calls(self):
        result = self.__run_test(msg.str_value.upper() == 'HELLO')
        self.assertEqual(len(result), 4, result)

    def test_get_set_values(self):
        result = self.__run_test(and_(set_value('somekey', msg.str_value), get_value('somekey') == 'hello'))
        self.assertEqual(len(result), 3, result)

    def test_has(self):
        result = self.__run_test(and_(has(msg.str_value, 'el'), get_value('cos/contains') == 'el'))
        self.assertEqual(len(result), 3, result)
        result = self.__run_test(and_(has(msg.str_value, 'el'), get_value('cos/contains') == 'ee'))
        self.assertEqual(len(result), 0, result)

    def test_regex(self):
        result = self.__run_test(and_(regex_search(msg.str_value, r'e[lL]lo'),
                                      get_value('cos/regex').group(0) == 'ello'))
        self.assertEqual(len(result), 3, result)
        result = self.__run_test(and_(regex_search(msg.str_value, r'e[lL]lo'),
                                      get_value('cos/regex').group(0) == 'eLlo'))
        self.assertEqual(len(result), 1, result)

    def test_coerce(self):
        result = self.__run_test(
            and_(regex_search(msg.str_value, r'The value is (\d+), which is expected to be less than'),
                 get_value('cos/regex').group(1) > 111))
        self.assertEqual(len(result), 1, result)

    @staticmethod
    def __run_test(condition):
        action = TestAction()
        Engine([Rule(condition, action)], simple_sequence).run()
        return action.collector
