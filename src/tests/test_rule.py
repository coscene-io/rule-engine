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

from rule_engine.rule import validate_rules_spec
from rule_engine.utils import ErrorSectionEnum


def _serialize_impl(str_arg, int_arg):
    pass


class TestRule(unittest.TestCase):
    def test_compile_and_validate_success(self):
        rule_spec = {
            "rules": [
                {
                    "conditions": [
                        "msg['temperature'] > 20",
                        "msg['humidity'] > 20",
                    ],
                    "actions": [
                        {
                            "name": "serialize",
                            "kwargs": {
                                "str_arg": "{msg['item']}",
                                "int_arg": 1,
                            },
                        },
                        {
                            "name": "serialize",
                            "kwargs": {
                                "str_arg": "{msg['item']}",
                                "int_arg": 1,
                            },
                        },
                    ],
                    "scopes": [],
                    "topics": ["test"],
                }
            ]
        }

        rules, result = validate_rules_spec(rule_spec, {})
        self.assertDictEqual(
            result.model_dump(exclude_unset=True),
            {
                "success": True,
                "errors": [],
            },
        )

    def test_compile_and_validate_empty_condition(self):
        rule_spec = {
            "rules": [
                {
                    "conditions": [
                        "",
                    ],
                    "actions": [
                        {
                            "name": "serialize",
                            "kwargs": {
                                "str_arg": "{msg['item']}",
                                "int_arg": 1,
                            },
                        },
                    ],
                    "scopes": [],
                    "topics": ["test"],
                }
            ]
        }
        rules, result = validate_rules_spec(rule_spec, {})
        self.assertDictEqual(
            result.model_dump(exclude_unset=True),
            {
                "success": False,
                "errors": [
                    {
                        "location": {
                            "ruleIndex": 0,
                            "section": ErrorSectionEnum.CONDITION,
                            "itemIndex": 0,
                        },
                        "syntaxError": {},
                    }
                ],
            },
        )

    def test_compile_and_validate_empty_action(self):
        rule_spec = {
            "rules": [
                {
                    "conditions": [
                        "msg['temperature'] > 20",
                    ],
                    "actions": [],
                    "scopes": [],
                    "topics": ["test"],
                }
            ]
        }
        rules, result = validate_rules_spec(rule_spec, {})
        self.assertDictEqual(
            result.model_dump(exclude_unset=True),
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
        rule_spec = {
            "rules": [
                {
                    "conditions": [
                        "msg['temperature'] > 20",
                        "msg['humidity'] > ",
                    ],
                    "actions": [
                        {
                            "name": "serialize",
                            "kwargs": {
                                "str_arg": "{msg['item']}",
                                "int_arg": 1,
                            },
                        },
                        {
                            "name": "serialize",
                            "kwargs": {
                                "str_arg": "{msg[}",
                                "int_arg": 1,
                            },
                        },
                        {
                            "name": "serialize",
                            "kwargs": {
                                "str_arg": "{msg['item']}",
                                "int_arg": 1,
                            },
                        },
                    ],
                    "scopes": [],
                    "topics": ["test"],
                }
            ]
        }
        rules, result = validate_rules_spec(rule_spec, {})
        self.assertDictEqual(
            result.model_dump(exclude_unset=True),
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
                ],
            },
        )
