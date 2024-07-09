import unittest

from rule_engine.expr.base_expr import and_, has, not_, or_
from rule_engine.expr.expr import Expr


class BaseExprTest(unittest.TestCase):
    def test_basic_bool_ops(self):
        testcases = [
            # test and
            ("test and 1", and_(True, True), True),
            ("test and 2", and_(True, False), False),
            ("test and 3", and_(False, True), False),
            ("test and 4", and_(False, False), False),
            ("test and 5", and_(Expr(True), True), True),
            ("test and 6", and_(Expr(True), False), False),
            ("test and 7", and_(Expr(False), True), False),
            ("test and 8", and_(Expr(False), False), False),
            ("test and 9", and_(True, Expr(True)), True),
            ("test and 10", and_(False, Expr(True)), False),
            ("test and 11", and_(True, Expr(False)), False),
            ("test and 12", and_(False, Expr(False)), False),
            ("test and 13", and_(Expr(True), Expr(True)), True),
            ("test and 14", and_(Expr(True), Expr(False)), False),
            ("test and 15", and_(Expr(False), Expr(True)), False),
            ("test and 16", and_(Expr(False), Expr(False)), False),
            # test or
            ("test or 1", or_(True, True), True),
            ("test or 2", or_(True, False), True),
            ("test or 3", or_(False, True), True),
            ("test or 4", or_(False, False), False),
            ("test or 5", or_(Expr(True), True), True),
            ("test or 6", or_(Expr(True), False), True),
            ("test or 7", or_(Expr(False), True), True),
            ("test or 8", or_(Expr(False), False), False),
            ("test or 9", or_(True, Expr(True)), True),
            ("test or 10", or_(False, Expr(True)), True),
            ("test or 11", or_(True, Expr(False)), True),
            ("test or 12", or_(False, Expr(False)), False),
            ("test or 13", or_(Expr(True), Expr(True)), True),
            ("test or 14", or_(Expr(True), Expr(False)), True),
            ("test or 15", or_(Expr(False), Expr(True)), True),
            ("test or 16", or_(Expr(False), Expr(False)), False),
            # test not
            ("test not 1", not_(True), False),
            ("test not 2", not_(False), True),
            ("test not 3", not_(Expr(True)), False),
            ("test not 4", not_(Expr(False)), True),
            # test has
            ("test has 1", has(Expr([1, 2, 3]), Expr(1)), True),
            ("test has 2", has(Expr([1, 2, 3]), Expr(4)), False),
            ("test has 3", has(Expr("abc"), Expr("a")), True),
            ("test has 4", has(Expr("abc"), Expr("d")), False),
        ]

        for name, expr, expected in testcases:
            with self.subTest(name):
                self.assertEqual(expr.value, expected)

    @staticmethod
    def __set_context(value):
        return lambda ctx: ctx.update({"key": value})

    def test_basic_bool_short_circuit(self):
        testcases = [
            # test and
            (
                "test and 1",
                and_(
                    Expr(True, self.__set_context(1)), Expr(True, self.__set_context(2))
                ),
                2,
            ),
            (
                "test and 2",
                and_(
                    Expr(True, self.__set_context(1)),
                    Expr(False, self.__set_context(2)),
                ),
                2,
            ),
            (
                "test and 3",
                and_(
                    Expr(False, self.__set_context(1)),
                    Expr(True, self.__set_context(2)),
                ),
                1,
            ),
            (
                "test and 4",
                and_(
                    Expr(False, self.__set_context(1)),
                    Expr(False, self.__set_context(2)),
                ),
                1,
            ),
            # test or
            (
                "test or 1",
                or_(
                    Expr(True, self.__set_context(1)),
                    Expr(True, self.__set_context(2)),
                ),
                1,
            ),
            (
                "test or 2",
                or_(
                    Expr(True, self.__set_context(1)),
                    Expr(False, self.__set_context(2)),
                ),
                1,
            ),
            (
                "test or 3",
                or_(
                    Expr(False, self.__set_context(1)),
                    Expr(True, self.__set_context(2)),
                ),
                2,
            ),
            (
                "test or 4",
                or_(
                    Expr(False, self.__set_context(1)),
                    Expr(False, self.__set_context(2)),
                ),
                2,
            ),
        ]
        for name, expr, expected in testcases:
            with self.subTest(name):
                ctx = dict()
                expr.eval(ctx)
                self.assertEqual(ctx["key"], expected)
