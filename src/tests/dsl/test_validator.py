import unittest

from ruleengine.dsl.validator import validate_condition, validate_action


class ValidatorTest(unittest.TestCase):
    def test_condition_validation(self):
        validate_condition("123")
        validate_condition("'hello'")
        validate_condition("topic_is('blah')")
        validate_condition("and_(topic_is('blah'), msg.something == 123)")

        with self.assertRaises(Exception):
            validate_condition("")

        with self.assertRaises(Exception):
            validate_condition("missing_function(123)")

        with self.assertRaises(Exception):
            # Actions should not be part of condition
            validate_condition("create_moment('hello')")

    def test_action_validation(self):
        validate_action("create_moment('hello')")
        validate_action("create_moment('hello', description='', duration=100)")
        validate_action("create_moment(msg.title, description='', duration=100)")
        validate_action("upload(title='hello', description='', before=1)")

        with self.assertRaises(Exception):
            # Mispelled action name
            validate_action("create_momen('hello')")

        with self.assertRaises(Exception):
            # Wrong keyword arg
            validate_action("create_moment('hello', descrin='', durion=100)")
