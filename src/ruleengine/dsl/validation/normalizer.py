import ast


def normalize_expression_tree(tree):
    return ast.fix_missing_locations(BooleanTransformer().visit(tree))


class BooleanTransformer(ast.NodeTransformer):
    def visit_JoinedStr(self, node):
        new_values = []
        condition_args = []
        for v in node.values:
            if isinstance(v, ast.Constant):
                new_values.append(v)
            elif isinstance(v, ast.FormattedValue):
                if v.format_spec:
                    if len(v.format_spec.values) != 1 or not isinstance(
                        v.format_spec.values[0], ast.Constant
                    ):
                        raise Exception("Formatting does not support nested values")

                new_values.append(
                    ast.FormattedValue(
                        ast.Name(f"arg{len(condition_args)}", ast.Load()),
                        v.conversion,
                        v.format_spec,
                    )
                )
                condition_args.append(self.generic_visit(v.value))
            else:
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

    def visit_Call(self, node):
        node = self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id in ("repeated", "debounce"):
            factory = self._eval_expr("lambda: ...")
            factory.body = node.args[0]
            node.args[0] = factory
        elif isinstance(node.func, ast.Name) and node.func.id in ("sequential", "timeout"):
            new_args = []
            for arg in node.args:
                factory = self._eval_expr("lambda: ...")
                factory.body = arg
                new_args.append(factory)
            node.args = new_args
        return node

    def visit_Compare(self, node):
        node = self.generic_visit(node)
        args = [node.left] + node.comparators
        param_list = ["arg" + str(i) for i in range(len(args))]
        condition_list = []
        for i, (left, right) in enumerate(zip(param_list, param_list[1:])):
            if isinstance(node.ops[i], ast.In):
                condition_list.append(self._eval_expr(f"has({right}, {left})"))
            elif isinstance(node.ops[i], ast.NotIn):
                condition_list.append(self._eval_expr(f"not_(has({right}, {left}))"))
            else:
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
