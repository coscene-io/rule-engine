# Copyright 2024 coScene
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
                    # In theory, f-strings format spec can be another
                    # f-string, but it makes our logic very clumsy, so we
                    # just don't support it for now. Check here that it's
                    # only a constant.
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
        # A hack since 1. conditions have states, and 2. within SequenceMatchCondition,
        # we need to create clean copies of the condition objects to avoid state
        # sharing. As a result, we need to transform the condition arguments
        # of the SequenceMatchCondition related functions to condition factories,
        # with which we can lazy create copies of the condition objects
        # within the SequenceMatchCondition.
        node = self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id in ("repeated", "debounce"):
            factory = self._eval_expr("lambda: ...")
            factory.body = node.args[0]
            node.args[0] = factory
        elif isinstance(node.func, ast.Name) and node.func.id in (
            "sequential",
            "timeout",
        ):
            new_args = []
            for arg in node.args:
                factory = self._eval_expr("lambda: ...")
                factory.body = arg
                new_args.append(factory)
            node.args = new_args
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
