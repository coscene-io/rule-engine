import unittest
from collections import namedtuple
from .dsl.actions import Action
from .dsl.base_conditions import *
from .engine import Rule, Engine

TestDataItem = namedtuple('TestDataItem', 'topic msg ts')
TestMessage = namedtuple('TestMessage', 'int_value str_value')

simple_sequence = [
    TestDataItem('t1', TestMessage(1, 'hello'), 0),
    TestDataItem('t2', TestMessage(2, 'hello'), 1),
    TestDataItem('t1', TestMessage(3, 'hello'), 2),
    TestDataItem('t2', TestMessage(4, 'hello'), 3),
    TestDataItem('t2', TestMessage(5, 'world'), 4),
]

class TestAction(Action):
    def __init__(self):
        self.collector = []

    def run(self, data):
        self.collector.append(data)

class FullEngineTest(unittest.TestCase):
    def test_topic_match(self):
        result = self.__run_test(topic_is('t1'))
        self.assertEqual(len(result), 2, result)

    def test_type_match(self):
        result = self.__run_test(type_is('TestMessage'))
        self.assertEqual(len(result), 5, result)

    def test_complex_conditions(self):
        result = self.__run_test(topic_is('t2') and msg.int_value > 3)
        self.assertEqual(len(result), 2, result)

    def test_function_calls(self):
        result = self.__run_test(msg.str_value.upper() == 'HELLO')
        self.assertEqual(len(result), 4, result)


    def __run_test(self, condition):
        action = TestAction()
        Engine([Rule(condition, action)], simple_sequence).run()
        return action.collector

