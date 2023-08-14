import unittest
from collections import namedtuple

from .dsl.actions import Action
from .dsl.base_conditions import always, and_, get_value, msg, set_value, topic_is
from .dsl.sequence_conditions import repeated, sequential, sustained
from .engine import Engine, Rule

TestDataItem = namedtuple('TestDataItem', 'topic msg ts')
TestMessage = namedtuple('TestMessage', 'int_value str_value')

simple_sequence = [
    TestDataItem('t1', TestMessage(1, 'hello'), 0),
    TestDataItem('t1', TestMessage(2, 'hello'), 0),
    TestDataItem('t2', TestMessage(1, 'hello'), 1),
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
    TestDataItem('t2', TestMessage(4, 'hello'), 7),
    TestDataItem('t2', TestMessage(4, 'hello'), 9),
]


class TestAction(Action):
    def __init__(self):
        self.collector = []

    def run(self, item, scope):
        self.collector.append((item, scope))


def get_start_times(res):
    return [i[1]['start_time'] for i in res]


class SequenceConditionTest(unittest.TestCase):
    def test_sustained_sequence(self):
        result = self.__run_test(sustained(always, msg.str_value == 'hello', 2))
        self.assertEqual(get_start_times(result), [0, 5])

        result = self.__run_test(sustained(always, msg.str_value == 'hello', 6))
        self.assertEqual(get_start_times(result), [])

        result = self.__run_test(sustained(topic_is('t1'), msg.str_value == 'hello', 2))
        self.assertEqual(get_start_times(result), [0])

        result = self.__run_test(sustained(topic_is('t1'), msg.str_value == 'hello', 6))
        self.assertEqual(get_start_times(result), [])

    def test_sequence_pattern(self):
        result = self.__run_test(sequential(
            and_(topic_is('t1'), msg.int_value == 1),
            and_(topic_is('t2'), (msg.int_value == 4), set_value('somekey', msg.int_value)),
            and_(topic_is('t2'), msg.int_value == get_value('somekey')),
            duration=4))
        self.assertEqual(get_start_times(result), [0])

        result = self.__run_test(sequential(
            and_(topic_is('t1'), msg.int_value == 1),
            and_(topic_is('t2'), (msg.int_value == 4), set_value('somekey', msg.int_value)),
            and_(topic_is('t2'), msg.int_value == get_value('somekey')),
            duration=2))
        self.assertEqual(get_start_times(result), [])

        # Overlapping sequences, and without duration
        result = self.__run_test(sequential(
            and_(topic_is('t1'), set_value('somekey', msg.int_value)),
            and_(topic_is('t2'), msg.int_value == get_value('somekey'))))
        self.assertEqual(get_start_times(result), [0, 0])

    def test_repeated(self):
        result = self.__run_test(repeated(always, 2, 5))
        self.assertEqual(get_start_times(result), [0])

        result = self.__run_test(repeated(topic_is('t2'), 2, 5))
        self.assertEqual(get_start_times(result), [1])

        result = self.__run_test(repeated(topic_is('t2'), 5, 5))
        self.assertEqual(get_start_times(result), [4])

        result = self.__run_test(repeated(topic_is('t2'), 2, 0.5))
        self.assertEqual(get_start_times(result), [1, 3, 4, 7])

    @staticmethod
    def __run_test(condition):
        action = TestAction()
        Engine([Rule(condition, action)], simple_sequence).run()
        return action.collector
