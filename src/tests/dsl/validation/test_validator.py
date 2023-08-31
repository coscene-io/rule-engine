import unittest

from ruleengine.dsl.validation.validator import validate_condition, validate_action
from ruleengine.dsl.validation.validation_result import ValidationErrorType


class ValidatorTest(unittest.TestCase):
    def test_condition_validation(self):
        self.assertTrue(validate_condition("msg").success)
        self.assertTrue(validate_condition("topic_is('blah')").success)
        self.assertTrue(validate_condition("and_(topic_is('blah'), msg.something == 123)").success)

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

        c = validate_condition("msg.123")
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.SYNTAX)

        c = validate_condition("msg.blah(   ")
        self.assertFalse(c.success)
        self.assertEqual(c.error_type, ValidationErrorType.SYNTAX)

        # c = validate_condition("missing_function(123)")

        # with self.assertRaises(Exception):
        #     # Actions should not be part of condition
        #     validate_condition("create_moment('hello')")

    def test_action_validation(self):
        pass
        # validate_action("create_moment('hello')")
        # validate_action("create_moment('hello', description='', duration=100)")
        # validate_action("create_moment(msg.title, description='', duration=100)")
        # validate_action("upload(title='hello', description='', before=1)")

        # with self.assertRaises(Exception):
        #     # Mispelled action name
        #     validate_action("create_momen('hello')")

        # with self.assertRaises(Exception):
        #     # Wrong keyword arg
        #     validate_action("create_moment('hello', descrin='', durion=100)")
