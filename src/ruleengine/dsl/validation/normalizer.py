import ast


def normalize_expression_tree(tree):
    return ast.fix_missing_locations(BooleanTransformer().visit(tree))


class BooleanTransformer(ast.NodeTransformer):
    def visit_JoinedStr(self, node):
        new_values = []
        condition_args = []
        for v in node.values:
            match v:
                case ast.Constant(value):
                    new_values.append(v)
                case ast.FormattedValue(value, conversion, format_spec):
                    if format_spec:
                        # In theory, f-strings format spec can be another
                        # f-string, but it makes our logic very clumsy, so we
                        # just don't support it for now. Check here that it's
                        # only a constant.
                        if len(format_spec.values) != 1 or not isinstance(
                            format_spec.values[0], ast.Constant
                        ):
                            raise Exception("Formatting does not support nested values")

                    new_values.append(
                        ast.FormattedValue(
                            ast.Name(f"arg{len(condition_args)}", ast.Load()),
                            conversion,
                            format_spec,
                        )
                    )
                    condition_args.append(self.generic_visit(value))
                case _:
                    raise Exception(f"Shouldn't get here: {v}")

        lambda_node = self._eval_expr(
            f"lambda {','.join(f'arg{i}' for i in range(len(condition_args)))}: ..."
        )
        lambda_node.body = ast.JoinedStr(new_values)
        return ast.Call(
            ast.Name("func_apply", ast.Load()), [lambda_node] + condition_args, []
        )

    def visit_BoolOp(self, node):
        node = self.generic_visit(node)

        match node.op:
            case ast.And():
                func_name = "and_"
            case ast.Or():
                func_name = "or_"
            case _:
                return node
        return ast.Call(ast.Name(func_name, ast.Load()), node.values, [])

    def visit_UnaryOp(self, node):
        node = self.generic_visit(node)

        match node.op:
            case ast.Not():
                return ast.Call(ast.Name("not_", ast.Load()), [node.operand], [])
            case _:
                return node

    def visit_Call(self, node):
        # A hack since 1. conditions have states, and 2. within SequenceMatchCondition,
        # we need to create clean copies of the condition objects to avoid state
        # sharing. As a result, we need to transform the condition arguments
        # of the SequenceMatchCondition related functions to condition factories,
        # with which we can lazy create copies of the condition objects
        # within the SequenceMatchCondition.
        node = self.generic_visit(node)

        match node.func:
            case ast.Name("repeated" | "debounce", ast.Load()):
                factory = self._eval_expr("lambda: ...")
                factory.body = node.args[0]
                node.args[0] = factory
            case ast.Name("sequential" | "timeout", ast.Load()):
                new_args = []
                for arg in node.args:
                    factory = self._eval_expr("lambda: ...")
                    factory.body = arg
                    new_args.append(factory)
                node.args = new_args

        return node

    def visit_Compare(self, node):
        node = self.generic_visit(node)

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

        args = [node.left] + node.comparators
        param_list = ["arg" + str(i) for i in range(len(args))]
        condition_list = []
        for i, (left, right) in enumerate(zip(param_list, param_list[1:])):
            match node.ops[i]:
                case ast.In():
                    condition_list.append(self._eval_expr(f"has({right}, {left})"))
                case ast.NotIn():
                    condition_list.append(
                        self._eval_expr(f"not_(has({right}, {left}))")
                    )
                case _:
                    condition_list.append(
                        ast.Compare(
                            ast.Name(left, ast.Load()),
                            [node.ops[i]],
                            [ast.Name(right, ast.Load())],
                        )
                    )

        wrapper = self._eval_expr(f"lambda {','.join(param_list)}: ...")
        wrapper.body = ast.Call(ast.Name("and_", ast.Load()), condition_list, [])

        return ast.Call(wrapper, args, [])

    def _eval_expr(self, str_value):
        return ast.parse(str_value, mode="eval").body
