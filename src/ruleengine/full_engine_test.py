import unittest
from collections import namedtuple
from .dsl.actions import Action
from .dsl.base_conditions import *
from .engine import Rule, Engine

TestDataItem = namedtuple('topic msg ts')
TestMessage = namedtuple('int_value str_value')

simple_sequence = [
    TestDataItem('t1', TestMessage(1, 'hello'), 0),
    TestDataItem('t2', TestMessage(2, 'hello'), 1),
    TestDataItem('t1', TestMessage(3, 'hello'), 2),
    TestDataItem('t2', TestMessage(4, 'hello'), 3),
    TestDataItem('t2', TestMessage(5, 'hello'), 4),
]

class TestAction(Action):
    def __init__(self):
        self.collector = []

    def run(self, data):
        self.collector.append(data)

class FullEngineTest(unittest.TestCase):
    def test_topic_match(self):
        action = TestAction()
        Engine([Rule(topic_is('t1'), action)], simple_sequence).run()
        self.assertEqual(len(action.collector), 2, action.collector)

