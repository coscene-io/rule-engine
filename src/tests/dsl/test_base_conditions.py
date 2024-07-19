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

MockMessage = namedtuple("MockMessage", "int_value str_value list_value")

simple_sequence = [
    DiagnosisItem("t1", MockMessage(1, "hello", [0, 1]), 0, "MockMessage"),
    DiagnosisItem("t2", MockMessage(2, "hello", [0, 1, 2]), 1, "MockMessage"),
    DiagnosisItem("t1", MockMessage(3, "heLlo", [0, 1, 2, 3]), 2, "MockMessage"),
    DiagnosisItem("t2", MockMessage(4, "hello", [0, 1, 2, 3, 4]), 3, "MockMessage"),
    DiagnosisItem("t2", MockMessage(5, "world", [0, 1, 2, 3, 4, 5]), 4, "MockMessage"),
    DiagnosisItem(
        "t3",
        MockMessage(5, "The value is 324, which is expected to be less than 22", []),
        5,
        "MockMessage",
    ),
    DiagnosisItem(
        "t3",
        MockMessage(5, "The value is 11, which is expected to be less than 22", []),
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
        result = self.__run_test("always")
        self.assertEqual(len(result), 7, result)

    def test_msg(self):
        result = self.__run_test('msg == MockMessage(1, "hello", [0, 1])')
        self.assertEqual(len(result), 1, result)

    def test_ts(self):
        result = self.__run_test("ts == 0")
        self.assertEqual(len(result), 1, result)

    def test_topic(self):
        result = self.__run_test('topic == "t1"')
        self.assertEqual(len(result), 2, result)

    def test_msgtype(self):
        result = self.__run_test('msgtype == "MockMessage"')
        self.assertEqual(len(result), 7, result)

        result = self.__run_test('msgtype == "FalseMessage"')
        self.assertEqual(len(result), 0, result)

    def test_none_values(self):
        result = self.__run_test('msg.this.doesnt.exist == "MockMessage"')
        self.assertEqual(len(result), 0, result)

        result = self.__run_test("is_none(msg.this.doesnt.exist)")
        self.assertEqual(len(result), 7, result)

    def test_list_values(self):
        result = self.__run_test("msg.list_value[2] == 2")
        self.assertEqual(len(result), 4, result)

    def test_and(self):
        result = self.__run_test('msgtype == "MockMessage" and topic == "t1"')
        self.assertEqual(len(result), 2, result)

    def test_or(self):
        result = self.__run_test('ts == 1 or topic == "t1"')
        self.assertEqual(len(result), 3, result)

    def test_not(self):
        result = self.__run_test("not ts == 1")
        self.assertEqual(len(result), 6, result)

    def test_topic_match(self):
        result = self.__run_test('topic == "t1"')
        self.assertEqual(len(result), 2, result)

    def test_type_match(self):
        result = self.__run_test('msgtype == "MockMessage"')
        self.assertEqual(len(result), 7, result)

        result = self.__run_test('msgtype == "FalseMessage"')
        self.assertEqual(len(result), 0, result)

    def test_complex_conditions(self):
        result = self.__run_test('topic == "t2" and msg.int_value > 2')
        self.assertEqual(len(result), 2, result)

    def test_function_calls(self):
        result = self.__run_test('msg.str_value.upper() == "HELLO"')
        self.assertEqual(len(result), 4, result)

    def test_get_set_values(self):
        result = self.__run_test(
            'set_value("somekey", msg.str_value) and get_value("somekey") == "hello"'
        )
        self.assertEqual(len(result), 3, result)

        result = self.__run_test('get_value("non-exist-key") == 1')
        self.assertEqual(len(result), 0, result)

    def test_has(self):
        result = self.__run_test(
            '"el" in msg.str_value and get_value("cos/contains") == "el"'
        )
        self.assertEqual(len(result), 3, result)
        result = self.__run_test(
            '"el" in msg.str_value and get_value("cos/contains") == "ee"'
        )
        self.assertEqual(len(result), 0, result)

    def test_regex(self):
        result = self.__run_test(
            'regex(msg.str_value, r"e[lL]lo").group(0) == "ello"',
        )
        self.assertEqual(len(result), 3, result)
        result = self.__run_test(
            'regex(msg.str_value, r"e[lL]lo").group(0) == "eLlo"',
        )
        self.assertEqual(len(result), 1, result)

    def test_concat(self):
        result = self.__run_test(
            'concat(msg.str_value, "---", msg.int_value) == "hello---1"',
        )
        self.assertEqual(len(result), 1, result)

    def test_coerce(self):
        result = self.__run_test(
            """regex(
                msg.str_value,
                r"The value is (\\d+), which is expected to be less than",
            ).group(1) > 111""",
        )
        self.assertEqual(len(result), 1, result)

    @staticmethod
    def __run_test(expr_str):
        action = CollectAction()
        engine = Engine(
            [
                Rule(
                    [str_to_condition(expr_str, {"MockMessage": MockMessage})],
                    [action],
                    {},
                )
            ]
        )
        for item in simple_sequence:
            engine.consume_next(item)
        return action.collector
