import ast


class AstTransformer(ast.NodeTransformer):
    def visit_BoolOp(self, node):
        node = self.generic_visit(node)
        if isinstance(node.op, ast.And):
            func_name = "and_"
        elif isinstance(node.op, ast.Or):
            func_name = "or_"
        else:
            return node
        return ast.Call(ast.Name(func_name, ast.Load()), node.values, [])

    def visit_UnaryOp(self, node):
        node = self.generic_visit(node)
        if isinstance(node.op, ast.Not):
            return ast.Call(ast.Name("not_", ast.Load()), [node.operand], [])
        else:
            return node

    def visit_Compare(self, node):
        # We need to jump through quite a few hoops to keep inline with Python's
        # semantics for comparison operators, just so we can rewrite the `in`
        # operator into our `has` function call. Suppose you have the expression
        #
        #  a op1 b op2 c
        #
        # Python treats this as
        #
        #  a op1 b and b op2 c
        #
        # Except `b` must only be evaluated once. So we package the above into
        # the following:
        #
        # (lambda arg0, arg1, arg2:
        #   and_(
        #     arg0 op1 arg1,
        #     arg1 op2 arg2))(a, b, c)
        #
        # And if one of the operators happen to be an `in` operator, we swap it
        # out with a `has` call.

        node = self.generic_visit(node)
        args = [node.left] + node.comparators
        param_list = ["arg" + str(i) for i in range(len(args))]
        condition_list = []
        for i, (left, right) in enumerate(zip(param_list, param_list[1:])):
            if isinstance(node.ops[i], ast.In):
                condition_list.append(self.__eval_expr(f"has({right}, {left})"))
            elif isinstance(node.ops[i], ast.NotIn):
                condition_list.append(self.__eval_expr(f"not_(has({right}, {left}))"))
            else:
                condition_list.append(
                    ast.Compare(
                        ast.Name(left, ast.Load()),
                        [node.ops[i]],
                        [ast.Name(right, ast.Load())],
                    )
                )

        wrapper = self.__eval_expr(f"lambda {','.join(param_list)}: ...")
        wrapper.body = ast.Call(ast.Name("and_", ast.Load()), condition_list, [])
        return ast.Call(wrapper, args, [])

    @staticmethod
    def __eval_expr(str_value):
        return ast.parse(str_value, mode="eval").body
