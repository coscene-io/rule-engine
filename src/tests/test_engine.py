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
from functools import partial

from rule_engine.engine import Engine
from rule_engine.rule import spec_to_rules


class TestEngine(unittest.TestCase):
    @staticmethod
    def serialize_impl(str_arg, int_arg, result_buffer: list[dict]):
        result = {
            "str_arg": str_arg,
            "int_arg": int_arg,
        }
        result_buffer[0] = result

    @staticmethod
    def build_serialize_engine_from_spec(spec, buffer):
        return Engine(
            spec_to_rules(
                spec,
                {
                    "serialize": partial(
                        TestEngine.serialize_impl, result_buffer=buffer
                    ),
                },
            )
        )

    def test_engine_comprehensive_single_condition(self):
        spec = {
            "rules": [
                {
                    "conditions": [
                        "msg.code > 20",
                    ],
                    "actions": [
                        {
                            "name": "serialize",
                            "kwargs": {
                                "str_arg": "{msg.code}",
                                "int_arg": 1,
                            },
                        },
                    ],
                    "scopes": [],
                    "topics": ["test_topic"],
                }
            ]
        }
        result_buffer = [{}]
        engine = self.build_serialize_engine_from_spec(spec, result_buffer)

        engine.example_consume_next({"code": 20}, "test_topic", 0.0)
        self.assertDictEqual(
            result_buffer[0],
            {},
        )
        engine.example_consume_next({"code": 21}, "test_topic", 0.0)
        self.assertDictEqual(
            result_buffer[0],
            {
                "str_arg": "21",
                "int_arg": 1,
            },
        )
        engine.example_consume_next({"code": 22}, "test_topic", 0.0)
        self.assertDictEqual(
            result_buffer[0],
            {
                "str_arg": "22",
                "int_arg": 1,
            },
        )
        engine.example_consume_next({"code": 20}, "test_topic", 0.0)
        self.assertDictEqual(
            result_buffer[0],
            {
                "str_arg": "22",
                "int_arg": 1,
            },
        )

    def test_engine_comprehensive_multiple_conditions(self):
        spec = {
            "rules": [
                {
                    "conditions": ["msg.code > 20", "int(msg.level) <= int(3)"],
                    "actions": [
                        {
                            "name": "serialize",
                            "kwargs": {
                                "str_arg": "{msg.code}",
                                "int_arg": 1,
                            },
                        },
                    ],
                    "scopes": [{}],
                    "topics": ["test_topic"],
                }
            ]
        }
        result_buffer = [{}]
        engine = self.build_serialize_engine_from_spec(spec, result_buffer)

        engine.example_consume_next({"code": 21, "level": 4}, "test_topic", 0.0)
        self.assertDictEqual(
            result_buffer[0],
            {},
        )
        engine.example_consume_next({"code": 19, "level": 2}, "test_topic", 0.0)
        self.assertDictEqual(
            result_buffer[0],
            {},
        )
        engine.example_consume_next({"code": 19, "level": 4}, "test_topic", 0.0)
        self.assertDictEqual(
            result_buffer[0],
            {},
        )
        engine.example_consume_next({"code": 21, "level": 2}, "test_topic", 0.0)
        self.assertDictEqual(
            result_buffer[0],
            {
                "str_arg": "21",
                "int_arg": 1,
            },
        )
        engine.example_consume_next({"code": 23, "level": 1}, "test_topic", 0.0)
        self.assertDictEqual(
            result_buffer[0],
            {
                "str_arg": "23",
                "int_arg": 1,
            },
        )
        engine.example_consume_next({"code": 21, "level": 4}, "test_topic", 0.0)
        self.assertDictEqual(
            result_buffer[0],
            {
                "str_arg": "23",
                "int_arg": 1,
            },
        )
        engine.example_consume_next({"code": 19, "level": 2}, "test_topic", 0.0)
        self.assertDictEqual(
            result_buffer[0],
            {
                "str_arg": "23",
                "int_arg": 1,
            },
        )
        engine.example_consume_next({"code": 19, "level": 4}, "test_topic", 0.0)
        self.assertDictEqual(
            result_buffer[0],
            {
                "str_arg": "23",
                "int_arg": 1,
            },
        )
