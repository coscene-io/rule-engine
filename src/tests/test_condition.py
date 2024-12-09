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

import celpy

from rule_engine.condition import Condition

TestActivation = {
    "msg": celpy.adapter.json_to_cel(
        {"message": {"code": 200}, "lst": [{"code": 1}, {"code": 2}, {"code": 3}]}
    ),
    "scope": celpy.adapter.json_to_cel({"code": 200}),
    "topic": celpy.celtypes.StringType("/TestTopic"),
    "ts": celpy.celtypes.DoubleType(1234567890.123456),
}


class TestCondition(unittest.TestCase):
    def test_int_int(self):
        condition, _ = Condition.compile_and_validate(""" 1 == 1 """)
        self.assertTrue(condition.evaluate(TestActivation))

        condition, _ = Condition.compile_and_validate(""" 1 == 2 """)
        self.assertFalse(condition.evaluate(TestActivation))

    def test_int_other(self):
        condition, _ = Condition.compile_and_validate(""" 1 == "1" """)
        self.assertFalse(condition.evaluate(TestActivation))

        condition, _ = Condition.compile_and_validate(""" 1 == "2" """)
        self.assertFalse(condition.evaluate(TestActivation))

        condition, _ = Condition.compile_and_validate(""" 1 == 1.0 """)
        self.assertFalse(condition.evaluate(TestActivation))

        condition, _ = Condition.compile_and_validate(""" 1 == 2.0 """)
        self.assertFalse(condition.evaluate(TestActivation))

    def test_msg_int(self):
        condition, _ = Condition.compile_and_validate(""" msg.message.code == 200 """)
        self.assertTrue(condition.evaluate(TestActivation))

        condition, _ = Condition.compile_and_validate(""" msg.message.code == 201 """)
        self.assertFalse(condition.evaluate(TestActivation))

    def test_msg_other(self):
        condition, _ = Condition.compile_and_validate(""" msg.message.code == "200" """)
        self.assertFalse(condition.evaluate(TestActivation))

        condition, _ = Condition.compile_and_validate(""" msg.message.code == "201" """)
        self.assertFalse(condition.evaluate(TestActivation))

        condition, _ = Condition.compile_and_validate(""" msg.message.code == 200.0 """)
        self.assertFalse(condition.evaluate(TestActivation))

        condition, _ = Condition.compile_and_validate(""" msg.message.code == 201.0 """)
        self.assertFalse(condition.evaluate(TestActivation))

    def test_msg_cast_other(self):
        condition, _ = Condition.compile_and_validate(
            """ msg.message.code == int("200") """
        )
        self.assertTrue(condition.evaluate(TestActivation))

        condition, _ = Condition.compile_and_validate(
            """ msg.message.code == int("201") """
        )
        self.assertFalse(condition.evaluate(TestActivation))

        condition, _ = Condition.compile_and_validate(
            """ msg.message.code == int(200.0) """
        )
        self.assertTrue(condition.evaluate(TestActivation))

        condition, _ = Condition.compile_and_validate(
            """ msg.message.code == int(201.0) """
        )
        self.assertFalse(condition.evaluate(TestActivation))

    def test_msg_scope(self):
        condition, _ = Condition.compile_and_validate(
            """ msg.message.code == scope.code """
        )
        self.assertTrue(condition.evaluate(TestActivation))

        condition, _ = Condition.compile_and_validate(
            """ msg.message.code == scope.invalid_attr """
        )
        self.assertFalse(condition.evaluate(TestActivation))

    def test_invalid(self):
        condition, _ = Condition.compile_and_validate(""" mmm.message.code == 200 """)
        self.assertFalse(condition.evaluate(TestActivation))

    def test_map_contains(self):
        condition, _ = Condition.compile_and_validate(
            """ msg.lst.map(x, x.code).contains(2) """
        )
        self.assertTrue(condition.evaluate(TestActivation))

        condition, _ = Condition.compile_and_validate(
            """ msg.lst.map(x, x.code).contains(4) """
        )
        self.assertFalse(condition.evaluate(TestActivation))

        condition, _ = Condition.compile_and_validate(
            """ msg.lst.map(x, x.code * 2).contains(6) """
        )
        self.assertTrue(condition.evaluate(TestActivation))

        condition, _ = Condition.compile_and_validate(
            """ msg.lst.map(x, x.code * 2).contains(7) """
        )
        self.assertFalse(condition.evaluate(TestActivation))

    def test_exists(self):
        condition, _ = Condition.compile_and_validate(
            """ msg.lst.exists(x, x.code == 2) """
        )
        self.assertTrue(condition.evaluate(TestActivation))

        condition, _ = Condition.compile_and_validate(
            """ msg.lst.exists(x, x.code == 4) """
        )
        self.assertFalse(condition.evaluate(TestActivation))

        condition, _ = Condition.compile_and_validate(
            """ msg.lst.exists(x, x.code * 2 == 6) """
        )
        self.assertTrue(condition.evaluate(TestActivation))

        condition, _ = Condition.compile_and_validate(
            """ msg.lst.exists(x, x.code * 2 == 7) """
        )
        self.assertFalse(condition.evaluate(TestActivation))

    def test_compile_and_validate(self):
        _, err = Condition.compile_and_validate("""msg.message.code == """)
        self.assertIsNotNone(err)

        _, err = Condition.compile_and_validate("""msg[0 """)
        self.assertIsNotNone(err)
