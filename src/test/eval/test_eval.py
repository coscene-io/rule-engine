import unittest

from rule_engine.eval.eval import eval_expression, inject_item_values, parse_expr
from rule_engine.expr import base_dsl_values


class EvalTest(unittest.TestCase):
    def eval_test(self, expr_str: str, item: any, expected: any):
        if isinstance(expected, Exception):
            with self.assertRaises(expected.__class__) as cm:
                parsed_expr = parse_expr(expr_str)
                injected_values = inject_item_values(item, base_dsl_values)
                eval_expression(parsed_expr, injected_values, {})
            self.assertEqual(str(cm.exception), str(expected))
            return
        parsed_expr = parse_expr(expr_str)
        injected_values = inject_item_values(item, base_dsl_values)
        self.assertEqual(eval_expression(parsed_expr, injected_values, {}), expected)

    def test_basic_eval(self):
        test_cases = [
            ("1", 1),
            ("(1 + 1) * (2 + 2) == 8", True),
            ("(1 + 1) * (2 + 2) == 9", False),
            ("(1 + 1) > 1", True),
            ("True and False", False),
            ("True or False", True),
            ("not True", False),
            ("not False", True),
            ("True and 1", 1),
            ("False and 1", False),
            ("True or 1", True),
            ("False or 1", 1),
            ("'aaa' in 'aaabcd'", True),
        ]
        for expr_str, expected in test_cases:
            with self.subTest(expr_str):
                self.eval_test(expr_str, {}, expected)

    def test_msg_eval(self):
        item = {
            "msg": {
                "msg": "log message",
            },
            "custom": [
                {
                    "aaa": [1, 2],
                },
                {
                    "aaa": [3, 4],
                },
            ],
            "ts": 3,
            "topic": "test topic",
            "msgtype": "rosgraph_msgs/Log",
        }
        test_cases = [
            # Basic expressions
            ("msg.msg", "log message"),
            ("ts", 3),
            ("topic", "test topic"),
            ("msgtype", "rosgraph_msgs/Log"),
            ("log", "log message"),
            ("msg.aaa", None),
            ("msg", {"msg": "log message"}),
            ("item.custom[0].aaa[0]", 1),
            ("item.custom[0].aaa[2]", None),
            # Complex expressions
            ("item.custom[0].aaa[0] + 1", 2),
            ("+item.custom[0].aaa[0]", 1),
            ("-item.custom[0].aaa[0]", -1),
            ("-(-item.custom[0].aaa[0])", 1),
            ("'mes' in msg.msg", True),
            ("msg.msg in 'log message and other'", True),
            ("'mes' in log", True),
            ("log in 'log message and other'", True),
            ("ts < 4", True),
            ("ts >= 5", False),
            ("ts < 4 and 'mes' in log", True),
            ("ts < 4 and 'mes' not in log", False),
            ("ts < 4 and True and True", True),
            ("aaa", SyntaxError("NameError: name 'aaa' is not defined")),
        ]
        for expr_str, expected in test_cases:
            with self.subTest(expr_str):
                self.eval_test(expr_str, item, expected)
