import unittest

from rule_engine.expr.expr import Expr


class ExprTest(unittest.TestCase):
    def test_expr_ops(self):
        testcases: list[tuple[str, any, bool]] = [
            # test eq
            ("test eq 1", Expr("1") == "1", True),
            ("test eq 2", "1" == Expr("1"), True),
            ("test eq 3", Expr("1") == "2", False),
            ("test eq 4", "1" == Expr("2"), False),
            ("test eq 5", Expr("1") == Expr("1"), True),
            ("test eq 6", Expr("1") == Expr("2"), False),
            ("test eq 7", Expr("1") == Expr(None), None),
            # test ne
            ("test ne 1", Expr(1) != 1, False),
            ("test ne 2", 1 != Expr(1), False),
            ("test ne 3", Expr(1) != 2, True),
            ("test ne 4", 1 != Expr(2), True),
            ("test ne 5", Expr("1") != Expr("2"), True),
            ("test ne 6", Expr("1") != Expr("1"), False),
            ("test ne 7", Expr("1") != Expr(None), None),
            # test lt
            ("test lt 1", Expr(1) < 2, True),
            ("test lt 2", 1 < Expr(2), True),
            ("test lt 3", Expr(2) < 1, False),
            ("test lt 4", 2 < Expr(1), False),
            ("test lt 5", Expr("1") < Expr("2"), True),
            ("test lt 6", Expr("2") < Expr("1"), False),
            ("test lt 7", Expr("1s") < Expr("2"), None),
            ("test lt 8", Expr("1") < Expr(None), None),
            # test le
            ("test le 1", Expr(1) <= 2, True),
            ("test le 2", 1 <= Expr(2), True),
            ("test le 3", Expr(2) <= 1, False),
            ("test le 4", 2 <= Expr(1), False),
            ("test le 5", Expr("1") <= Expr("2"), True),
            ("test le 6", Expr("2") <= Expr("1"), False),
            ("test le 7", Expr("1s") <= Expr("2"), None),
            ("test le 8", Expr("1") <= Expr(None), None),
            # test gt
            ("test gt 1", Expr(2) > 1, True),
            ("test gt 2", 2 > Expr(1), True),
            ("test gt 3", Expr(1) > 2, False),
            ("test gt 4", 1 > Expr(2), False),
            ("test gt 5", Expr("2") > Expr("1"), True),
            ("test gt 6", Expr("1") > Expr("2"), False),
            ("test gt 7", Expr("1s") > Expr("2"), None),
            ("test gt 8", Expr("1") > Expr(None), None),
            # test ge
            ("test ge 1", Expr(2) >= 1, True),
            ("test ge 2", 2 >= Expr(1), True),
            ("test ge 3", Expr(1) >= 2, False),
            ("test ge 4", 1 >= Expr(2), False),
            ("test ge 5", Expr("2") >= Expr("1"), True),
            ("test ge 6", Expr("1") >= Expr("2"), False),
            ("test ge 7", Expr("1s") >= Expr("2"), None),
            ("test ge 8", Expr("1") >= Expr(None), None),
            # test pos
            ("test pos 1", +Expr(1), 1),
            ("test pos 2", +Expr(-1), -1),
            ("test pos 3", +Expr("1"), None),
            ("test pos 4", +Expr(None), None),
            # test neg
            ("test neg 1", -Expr(1), -1),
            ("test neg 2", -Expr(-1), 1),
            ("test neg 3", -Expr("1"), None),
            ("test neg 4", -Expr(None), None),
            # test add and radd
            ("test add 1", Expr(1) + 2, 3),
            ("test add 2", 1 + Expr(2), 3),
            ("test add 3", Expr(1) + Expr(2), 3),
            ("test add 4", Expr("1") + Expr("2"), 3),
            ("test add 5", Expr("1s") + Expr("2"), None),
            ("test add 6", Expr("1") + Expr(None), None),
            # test sub and rsub
            ("test sub 1", Expr(1) - 2, -1),
            ("test sub 2", 1 - Expr(2), -1),
            ("test sub 3", Expr(1) - Expr(2), -1),
            ("test sub 4", Expr("1") - Expr("2"), -1),
            ("test sub 5", Expr("1s") - Expr("2"), None),
            ("test sub 6", Expr("1") - Expr(None), None),
            # test mul and rmul
            ("test mul 1", Expr(1) * 2, 2),
            ("test mul 2", 1 * Expr(2), 2),
            ("test mul 3", Expr(1) * Expr(2), 2),
            ("test mul 4", Expr("1") * Expr("2"), 2),
            ("test mul 5", Expr("1s") * Expr("2"), None),
            ("test mul 6", Expr("1") * Expr(None), None),
            # test truediv and rtruediv
            ("test truediv 1", Expr(1) / 2, 0.5),
            ("test truediv 2", 1 / Expr(2), 0.5),
            ("test truediv 3", Expr(1) / Expr(2), 0.5),
            ("test truediv 4", Expr("1") / Expr("2"), 0.5),
            ("test truediv 5", Expr("1s") / Expr("2"), None),
            ("test truediv 6", Expr("1") / Expr(None), None),
            # test getattr
            ("test getattr 1", Expr({"a": 1}).a, 1),
            ("test getattr 2", Expr({"a": 1}).b, None),
            ("test getattr 3", Expr({"a": 1}).b.c, None),
            ("test getattr 4", Expr({"a": 1}).a.b, None),
            # test getitem
            ("test getitem 1", Expr([1, 2])[0], 1),
            ("test getitem 2", Expr([1, 2])[1], 2),
            ("test getitem 3", Expr([1, 2])[2], None),
            ("test getitem 4", Expr([1, 2])[0][0], None),
            # test complex getattr and getitem
            ("test complex 1", Expr({"a": [{"b": 1}, {"b": 2}]}).a[0].b, 1),
            ("test complex 2", Expr({"a": [{"b": 1}, {"b": 2}]}).a[1].b, 2),
            ("test complex 3", Expr({"a": [{"b": 1}, {"b": 2}]}).a[2].b, None),
            ("test complex 4", Expr({"a": [{"b": 1}, {"b": 2}]}).a[0].c, None),
            ("test complex 5", Expr({"a": [{"b": 1}, {"b": 2}]}).a[0].b.c, None),
            ("test complex 6", Expr({"a": [{"b": 1}, {"b": 2}]}).a[0].b[0], None),
        ]

        for name, expr, expected in testcases:
            with self.subTest(name):
                result = expr.eval({})
                self.assertEqual(result, expected)

    @staticmethod
    def __update_ctx(key, value):
        return lambda ctx: ctx.update({key: value})

    def test_expr_callbacks(self):
        testcases: list[tuple[str, any, list[tuple[str, any]]]] = [
            (
                "test single callback 1",
                Expr("1", self.__update_ctx("a", 1)) == "1",
                [("a", 1)],
            ),
            (
                "test single callback 2",
                1 == Expr("1", self.__update_ctx("a", 1)),
                [("a", 1)],
            ),
            (
                "test multiple callback",
                Expr("1", self.__update_ctx("a", 1))
                == Expr("1", self.__update_ctx("b", 2)),
                [("a", 1), ("b", 2)],
            ),
            (
                "test none callback 1",
                1 < Expr("1s", self.__update_ctx("a", 1)),
                [("a", None)],
            ),
            (
                "test none callback 2",
                1 < Expr("1", self.__update_ctx("a", 1)).a,
                [("a", None)],
            ),
            (
                "test none callback 3",
                Expr("1", self.__update_ctx("a", 1))
                == Expr(None, self.__update_ctx("b", 2)),
                [("a", None), ("b", None)],
            ),
        ]
        for name, expr, key_values in testcases:
            with self.subTest(name):
                ctx = {}
                expr.eval(ctx)
                for key, value in key_values:
                    self.assertEqual(ctx.get(key), value)
