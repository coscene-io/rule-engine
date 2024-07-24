# Copyright 2024 coScene
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from collections import namedtuple

from ruleengine.dsl.action import Action
from ruleengine.engine import DiagnosisItem, Engine, Rule
from tests.dsl.utils import str_to_condition

MockMessage = namedtuple("MockMessage", "int_value str_value")
RosMockMessage = namedtuple("RosMockMessage", "msg level")
FoxgloveMockMessage = namedtuple("FoxgloveMockMessage", "message level")

simple_sequence = [
    DiagnosisItem("t1", MockMessage(1, "hello"), 0, "MockMessage"),
    DiagnosisItem("t2", MockMessage(2, "hello"), 1, "MockMessage"),
    DiagnosisItem("t1", RosMockMessage("ros log message 1", 3), 2, "rosgraph_msgs/Log"),
    DiagnosisItem("t1", RosMockMessage("ros log message 1", 4), 3, "rosgraph_msgs/Log"),
    DiagnosisItem("t1", RosMockMessage("ros log message 1", 7), 4, "MockMessage"),
    DiagnosisItem(
        "t2", FoxgloveMockMessage("foxglove log message 1", 2), 5, "foxglove_msgs/Log"
    ),
    DiagnosisItem(
        "t2", FoxgloveMockMessage("foxglove log message 2", 3), 6, "foxglove.Log"
    ),
    DiagnosisItem(
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
        result = self.__run_test('log != ""')
        self.assertEqual(len(result), 5, result)

        result = self.__run_test('log == "ros log message 1"')
        self.assertEqual(len(result), 2, result)

        result = self.__run_test('"foxglove log message" in log')
        self.assertEqual(len(result), 3, result)

    def test_log_level(self):
        result = self.__run_test("log_level == LogLevel.DEBUG")
        self.assertEqual(len(result), 0, result)

        result = self.__run_test("log_level == LogLevel.INFO")
        self.assertEqual(len(result), 1, result)

        result = self.__run_test("log_level == LogLevel.WARN")
        self.assertEqual(len(result), 2, result)

        result = self.__run_test("log_level == LogLevel.UNKNOWN")
        self.assertEqual(len(result), 5, result)

    @staticmethod
    def __run_test(expr_str):
        action = CollectAction()
        engine = Engine([Rule([str_to_condition(expr_str)], [action], {})])
        for item in simple_sequence:
            engine.consume_next(item)
        return action.collector
