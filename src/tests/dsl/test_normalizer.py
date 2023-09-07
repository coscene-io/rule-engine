import ast
import unittest

from ruleengine.dsl.validation.normalizer import normalize_expression_tree

class NormalizerTest(unittest.TestCase):
    def test_transform_boolean_ops(self):
        self._assert_equivalent(
                'a and b and c',
                'and_(a, b, c)')

        self._assert_equivalent(
                'a or b or c',
                'or_(a, b, c)')

        self._assert_equivalent(
                'not a',
                'not_(a)')

        self._assert_equivalent(
                'a > 1 in b',
                'has(b, a)'
                )

        self._assert_equivalent(
                'a or b and c',
                'or_(a, and_(b, c))')


    def _assert_equivalent(self, original, normalized):
        left = normalize_expression_tree(ast.parse(original, mode='eval'))
        right = ast.parse(normalized, mode='eval')
        self.assertEqual(ast.unparse(left), ast.unparse(right))

