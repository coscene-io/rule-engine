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

from ruleengine.dsl.base_actions import noop
from ruleengine.dsl.validation.validation_result import ValidationErrorType
from ruleengine.dsl.validation.validator import validate_action, validate_condition


class ValidatorTest(unittest.TestCase):
    def test_condition_validation(self):
        self.assertTrue(validate_condition("msg").success)
        self.assertTrue(validate_condition("msg.aaa").success)
        self.assertTrue(validate_condition("topic == 'blah'").success)
        self.assertTrue(
            validate_condition("and_(topic == 'blah', msg.something == 123)").success
        )

        c = validate_condition("    ")
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.EMPTY)

        c = validate_condition("123")
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.NOT_CONDITION)
        self.assertEqual(c.details["actual"], "int")

        c = validate_condition("'hello'")
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.NOT_CONDITION)
        self.assertEqual(c.details["actual"], "str")

        c = validate_condition("return 1")
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.SYNTAX)

        c = validate_condition("import json")
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.SYNTAX)

        c = validate_condition("msg.123")
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.SYNTAX)

        c = validate_condition("msg.blah(   ")
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.SYNTAX)

        c = validate_condition("missing_function(123)")
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.UNDEFINED)
        self.assertEqual(c.details["name"], "missing_function")

        c = validate_condition("missing_thing.field")
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.UNDEFINED)
        self.assertEqual(c.details["name"], "missing_thing")

        # Actions should not be part of condition
        c = validate_condition("create_moment('hello')")
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.UNDEFINED)
        self.assertEqual(c.details["name"], "create_moment")

        # Builtin functions are forbidden unless whitelisted
        c = validate_condition("open('some file')")
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.UNDEFINED)
        self.assertEqual(c.details["name"], "open")

        c = validate_condition("eval('123')")
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.UNDEFINED)
        self.assertEqual(c.details["name"], "eval")

    def test_action_validation(self):
        self.assertTrue(validate_action("create_moment('hello')", noop).success)
        self.assertTrue(
            validate_action("create_moment('hello', description='')", noop).success
        )
        self.assertTrue(
            validate_action("create_moment(msg.title, description='')", noop).success
        )
        self.assertTrue(
            validate_action(
                "upload(title='hello', description='', before=1)", noop
            ).success
        )
        self.assertTrue(
            validate_action(
                "upload(title='hello', description='', after=1)", noop
            ).success
        )

        c = validate_action("create_moment('hello', duration='', 'something')", noop)
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.SYNTAX)

        c = validate_action("msg.field == 1", noop)
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.NOT_ACTION)
        self.assertIn("Condition", c.details["actual"])

        # Wrong keyword arg
        c = validate_action("create_moment('hello', descrin='')", noop)
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.UNDEFINED)
        self.assertEqual("descrin", c.details["name"])

        # Wrong positional arg, too few or too many
        c = validate_action("create_moment()", noop)
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.UNKNOWN)
        self.assertIn("title", c.details["message"])

        c = validate_action("create_moment(1, 2, 3, 4, 5, 6, 7, 8, 9)", noop)
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.UNKNOWN)
        self.assertIn("too many", c.details["message"])

        c = validate_action("upload('', title='')", noop)
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.UNKNOWN)
        self.assertIn("multiple values", c.details["message"])

        # Wrong arg type
        c = validate_action("create_moment('hello', assign_to=1)", noop)
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.UNKNOWN)
        self.assertIn("assign_to", c.details["message"])

        c = validate_action("upload(extra_files=1)", noop)
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.UNKNOWN)
        self.assertIn("extra_files", c.details["message"])

        c = validate_action("upload(extra_files=[1])", noop)
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.UNKNOWN)
        self.assertIn("extra_files", c.details["message"])

        c = validate_action("upload(labels=1)", noop)
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.UNKNOWN)
        self.assertIn("labels", c.details["message"])

        c = validate_action("upload(labels=[1])", noop)
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.UNKNOWN)
        self.assertIn("labels", c.details["message"])
