import ast
import unittest

from ruleengine.dsl.validation.normalizer import normalize_expression_tree


class NormalizerTest(unittest.TestCase):
    def test_transform_boolean_ops(self):
        self._assert_equivalent("a and b and c", "and_(a, b, c)")

        self._assert_equivalent("a or b or c", "or_(a, b, c)")

        self._assert_equivalent("a or b and c", "or_(a, and_(b, c))")

        self._assert_equivalent("not a", "not_(a)")

        self._assert_equivalent(
            "not not a or b and c", "or_(not_(not_(a)), and_(b, c))"
        )

        self._assert_equivalent(
            "a in b", "(lambda arg0, arg1: and_(has(arg1, arg0)))(a, b)"
        )

        self._assert_equivalent(
            "a > 1 in b",
            "(lambda arg0, arg1, arg2: and_(arg0 > arg1, has(arg2, arg1)))(a, 1, b)",
        )

        self._assert_equivalent(
            "c or a > 1 in b and d",
            "or_(c, and_((lambda arg0, arg1, arg2: and_(arg0 > arg1, has(arg2, arg1)))(a, 1, b), d))",
        )

    def _assert_equivalent(self, original, normalized):
        left = normalize_expression_tree(ast.parse(original, mode="eval"))
        right = ast.parse(normalized, mode="eval")
        self.assertEqual(ast.unparse(left), ast.unparse(right))
