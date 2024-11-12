import unittest
from functools import partial

import celpy

from rule_engine.action import Action, compile_embedded_expr

TestActivation = {
    "msg": celpy.adapter.json_to_cel({"message": {"code": "200"}}),
    "scope": celpy.adapter.json_to_cel({"code": "200"}),
    "topic": celpy.celtypes.StringType("/TestTopic"),
    "ts": celpy.celtypes.DoubleType(1234567890.123456),
}


class TestAction(unittest.TestCase):
    @staticmethod
    def serialize_impl(
        str_arg, int_arg, bool_arg, other_str_arg, action_result: list[str]
    ):
        result = {
            "str_arg": str_arg,
            "int_arg": int_arg,
            "bool_arg": bool_arg,
            "other_str_arg": other_str_arg,
        }
        action_result[0] = str(result)

    @staticmethod
    def get_action(raw_kwargs, action_result):
        return Action(
            name="serialize",
            raw_kwargs=raw_kwargs,
            impl=partial(TestAction.serialize_impl, action_result=action_result),
        )

    def test_simple(self):
        action_result = [""]
        action = self.get_action(
            {
                "str_arg": "hello",
                "int_arg": 123,
                "bool_arg": True,
                "other_str_arg": "world",
            },
            action_result,
        )

        self.assertEqual("", action_result[0])
        action.run(TestActivation)
        self.assertEqual(
            "{'str_arg': 'hello', 'int_arg': 123, 'bool_arg': True, 'other_str_arg': 'world'}",
            action_result[0],
        )

    def test_single(self):
        action_result = [""]
        action = self.get_action(
            {
                "str_arg": "aaa{ msg.message.code } bbb",
                "int_arg": 123,
                "bool_arg": True,
                "other_str_arg": "worl{ scope.invalid_attr }d",
            },
            action_result,
        )

        self.assertEqual("", action_result[0])
        action.run(TestActivation)
        self.assertEqual(
            "{'str_arg': 'aaa200 bbb', 'int_arg': 123, 'bool_arg': True, 'other_str_arg': 'worl{ ERROR }d'}",
            action_result[0],
        )

    def test_validation(self):
        action = self.get_action(
            {
                "str_arg": "hello",
                "int_arg": 123,
                "bool_arg": True,
                "other_str_arg": "world",
            },
            [""],
        )
        self.assertTrue(action.validation_result)

        action = self.get_action(
            {
                "str_arg": "hello",
                "int_arg": 123,
                "bool_arg": True,
                "other_str_arg": "wor{ 1+ }ld",
            },
            [""],
        )
        self.assertFalse(action.validation_result)


class TestEvaluateEmbeddedExpression(unittest.TestCase):
    def assert_expression(self, expr, activation, expected):
        """
        Helper function
        Assert that the expression evaluates to the expected value
        """
        evaluated = compile_embedded_expr(expr)
        self.assertEqual(evaluated(activation), expected)

    def test_simple(self):
        expression = "A simple expression"
        self.assert_expression(expression, TestActivation, "A simple expression")

    def test_single(self):
        expression = "aaa { msg.code  } bbb"
        self.assert_expression(expression, TestActivation, "aaa { ERROR } bbb")

        expression = "aaa { msg.message.code } bbb"
        self.assert_expression(expression, TestActivation, "aaa 200 bbb")

    def test_multiple(self):
        expression = """
        aaa { msg.code }
        bbb { msg.message.code }
        ccc { scope.code }
        ddd { topic }
        eee { ts }
        """
        expected = """
        aaa { ERROR }
        bbb 200
        ccc 200
        ddd /TestTopic
        eee 1234567890.123456
        """
        self.assert_expression(expression, TestActivation, expected)
