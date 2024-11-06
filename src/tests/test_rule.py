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

from rule_engine.action import Action
from rule_engine.condition import Condition
from rule_engine.rule import Rule, validate_rules
from rule_engine.utils import ErrorSectionEnum


def _serialize_impl(str_arg, int_arg):
    pass


class TestEngine(unittest.TestCase):
    def test_compile_and_validate_success(self):
        rules = [
            Rule(
                [
                    Condition("msg['temperature'] > 20"),
                    Condition("msg['humidity'] > 20"),
                ],
                [
                    Action(
                        "serialize",
                        _serialize_impl,
                        {
                            "str_arg": "{msg['item']}",
                            "int_arg": 1,
                        },
                    ),
                    Action(
                        "serialize",
                        _serialize_impl,
                        {
                            "str_arg": "msg['item']",
                            "int_arg": 1,
                        },
                    ),
                ],
                {},
                "test",
            )
        ]
        self.assertDictEqual(
            validate_rules(rules).model_dump(exclude_unset=True),
            {
                "success": True,
                "errors": [],
            },
        )

    def test_compile_and_validate_empty_condition(self):
        rules = [
            Rule(
                [],
                [
                    Action(
                        "serialize",
                        _serialize_impl,
                        {
                            "str_arg": "{msg['item']}",
                            "int_arg": 1,
                        },
                    ),
                ],
                {},
                "test",
            )
        ]
        self.assertDictEqual(
            validate_rules(rules).model_dump(exclude_unset=True),
            {
                "success": False,
                "errors": [
                    {
                        "location": {
                            "ruleIndex": 0,
                            "section": ErrorSectionEnum.CONDITION,
                        },
                        "emptySection": {},
                    }
                ],
            },
        )

    def test_compile_and_validate_empty_action(self):
        rules = [
            Rule(
                [
                    Condition("msg['temperature'] > 20"),
                ],
                [],
                {},
                "test",
            )
        ]
        self.assertDictEqual(
            validate_rules(rules).model_dump(exclude_unset=True),
            {
                "success": False,
                "errors": [
                    {
                        "location": {
                            "ruleIndex": 0,
                            "section": ErrorSectionEnum.ACTION,
                        },
                        "emptySection": {},
                    }
                ],
            },
        )

    def test_compile_and_validate_multiple_errors(self):
        rules = [
            Rule(
                [
                    Condition("msg['temperature'] > 20"),
                    Condition("msg['humidity'] > "),
                ],
                [
                    Action(
                        "serialize",
                        _serialize_impl,
                        {
                            "str_arg": "{msg['item']}",
                            "int_arg": 1,
                        },
                    ),
                    Action(
                        "serialize",
                        _serialize_impl,
                        {
                            "str_arg": "{msg[}",
                            "int_arg": 1,
                        },
                    ),
                    Action(
                        "serialize",
                        _serialize_impl,
                        {
                            "str_arg2": "msg['item']",
                            "int_arg": 1,
                        },
                    ),
                ],
                {},
                "test",
            )
        ]
        self.assertDictEqual(
            validate_rules(rules).model_dump(exclude_unset=True),
            {
                "success": False,
                "errors": [
                    {
                        "location": {
                            "ruleIndex": 0,
                            "section": ErrorSectionEnum.CONDITION,
                            "itemIndex": 1,
                        },
                        "syntaxError": {},
                    },
                    {
                        "location": {
                            "ruleIndex": 0,
                            "section": ErrorSectionEnum.ACTION,
                            "itemIndex": 1,
                        },
                        "syntaxError": {},
                    },
                    {
                        "location": {
                            "ruleIndex": 0,
                            "section": ErrorSectionEnum.ACTION,
                            "itemIndex": 2,
                        },
                        "syntaxError": {},
                    },
                ],
            },
        )
