import ast


def normalize_expression_tree(tree):
    return ast.fix_missing_locations(BooleanTransformer().visit(tree))


class BooleanTransformer(ast.NodeTransformer):
    def visit_BoolOp(self, node):
        node = self.generic_visit(node)

        match node.op:
            case ast.And():
                func_name = "and_"
            case ast.Or():
                func_name = "or_"
            case _:
                raise Exception(f"Should not get here? {node.op}")
        return ast.Call(ast.Name(func_name, ast.Load()), node.values, [])

    def visit_UnaryOp(self, node):
        node = self.generic_visit(node)

        match node.op:
            case ast.Not():
                return ast.Call(ast.Name("not_", ast.Load()), [node.operand], [])
            case _:
                return node

    def visit_Compare(self, node):
        node = self.generic_visit(node)

        args = [node.left] + node.comparators
        param_list = ["arg" + str(i) for i in range(len(args))]
        condition_list = []
        for i, (left, right) in enumerate(zip(param_list, param_list[1:])):
            match node.ops[i]:
                case ast.In():
                    condition_list.append(
                        ast.parse(f"has({right}, {left})", mode="eval").body
                    )
                case ast.NotIn():
                    condition_list.append(
                        ast.parse(f"not(has({right}, {left}))", mode="eval").body
                    )
                case _:
                    condition_list.append(
                        ast.Compare(
                            ast.Name(left, ast.Load()),
                            [node.ops[i]],
                            [ast.Name(right, ast.Load())],
                        )
                    )

        parsed_wrapper = ast.parse(
            f"lambda {','.join(param_list)}: ...", mode="eval"
        ).body
        wrapper = ast.Lambda(
            parsed_wrapper.args,
            ast.Call(ast.Name("and_", ast.Load()), condition_list, []),
        )

        return ast.Call(wrapper, args, [])
