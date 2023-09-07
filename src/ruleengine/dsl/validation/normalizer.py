import ast

def normalize_expression_tree(tree):
    return ast.fix_missing_locations(BooleanTransformer().visit(tree))

class BooleanTransformer(ast.NodeTransformer):
    def visit_BoolOp(self, node):
        args = [self.generic_visit(v) for v in node.values]
        match node.op:
            case ast.And:
                func_name = 'and_'
            case ast.Or:
                func_name = 'or_'
            case _:
                raise Exception('Should not get here?')
        return ast.Call(
                ast.Name(func_name, ast.Load()),
                args
                )

    def visit_UnaryOp(self, node):
        match node.op:
            case ast.Not:
                operand = self.generic_visit(node.operand)
                return ast.Call(
                        ast.Name('not_', ast.Load()),
                        [operand])
            case _:
                return node

    def visit_Compare(self, node):
        # TODO
        return node

