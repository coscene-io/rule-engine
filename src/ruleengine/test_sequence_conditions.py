import unittest
from collections import namedtuple
from .dsl.actions import Action
from .dsl.base_conditions import *
from .dsl.sequence_conditions import *
from .engine import Rule, Engine

TestDataItem = namedtuple('TestDataItem', 'topic msg ts')
TestMessage = namedtuple('TestMessage', 'int_value str_value')

simple_sequence = [
    TestDataItem('t1', TestMessage(1, 'hello'), 0),
    TestDataItem('t2', TestMessage(2, 'hello'), 1),
    TestDataItem('t2', TestMessage(2, 'hello'), 1),
    TestDataItem('t1', TestMessage(3, 'hello'), 2),
    TestDataItem('t1', TestMessage(3, 'hello'), 3),
    TestDataItem('t2', TestMessage(4, 'hello'), 3),
    TestDataItem('t2', TestMessage(4, 'hello'), 3),
    TestDataItem('t2', TestMessage(5, 'world'), 4),
    TestDataItem('t2', TestMessage(5, 'world'), 4),
    TestDataItem('t2', TestMessage(4, 'hello'), 5),
    TestDataItem('t2', TestMessage(4, 'hello'), 6),
    TestDataItem('t2', TestMessage(4, 'hello'), 7),
    TestDataItem('t2', TestMessage(4, 'hello'), 9),
]

class TestAction(Action):
    def __init__(self):
        self.collector = []

    def run(self, item, scope):
        self.collector.append((item, scope))


class SequenceConditionTest(unittest.TestCase):
    def test_sustained_sequence(self):
        result = self.__run_test(sustained(always, msg.str_value == 'hello', 2))
        self.assertEqual(len(result), 2, result)

        result = self.__run_test(sustained(always, msg.str_value == 'hello', 6))
        self.assertEqual(len(result), 0, result)

        result = self.__run_test(sustained(topic_is('t1'), msg.str_value == 'hello', 2))
        self.assertEqual(len(result), 1, result)

        result = self.__run_test(sustained(topic_is('t1'), msg.str_value == 'hello', 6))
        self.assertEqual(len(result), 0, result)

    def __run_test(self, condition):
        action = TestAction()
        Engine([Rule(condition, action)], simple_sequence).run()
        return action.collector

