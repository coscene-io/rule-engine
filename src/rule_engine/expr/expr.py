import operator
from functools import wraps
from typing import Callable

from box import Box, BoxKeyError, BoxList
from box.exceptions import BoxValueError


class Expr:
    """
    This is the class for all expressions, with an additional callback, which
    is a thunk that is called when the expression is evaluated.
    """

    def __init__(self, value: any, callback: Callable[[dict], None] = None):
        self.value = value
        self.callback = callback

    def eval(self, ctx: dict) -> any:
        if self.callback is not None:
            self.callback(ctx)
        return self.value

    def __getattr__(self, item):
        try:
            boxed_value = (
                BoxList(self.value) if isinstance(self.value, list) else Box(self.value)
            )
            return Expr(boxed_value[item], self.callback)
        except (BoxKeyError, BoxValueError, IndexError):
            return Expr(None)

    def __getitem__(self, item):
        try:
            boxed_value = (
                BoxList(self.value) if isinstance(self.value, list) else Box(self.value)
            )
            return Expr(boxed_value[item], self.callback)
        except (BoxKeyError, BoxValueError, IndexError):
            return Expr(None)

    @staticmethod
    def wrap(v: any) -> "Expr":
        """
        Wraps a value into an Expr if it is not already an Expr.
        """
        if isinstance(v, Expr):
            return v
        return Expr(v)

    @staticmethod
    def wrap_args(func):
        """
        Decorator that calls wrap on all the args of a function.
        """

        @wraps(func)
        def result_func(*args, **kwargs):
            args = [Expr.wrap(value) for value in args]
            kwargs = {key: Expr.wrap(value) for key, value in kwargs.items()}
            return func(*args, **kwargs)

        return result_func

    def __wrap_binary_op(
        self,
        other: any,
        op: Callable[[any, any], any],
        coerce: Callable[[any], any] = lambda x: x,
        swap: bool = False,
    ) -> "Expr":
        other_wrapped = Expr.wrap(other)
        if other_wrapped.value is None or self.value is None:
            return Expr(None)
        try:
            return Expr(
                value=(
                    op(coerce(other_wrapped.value), coerce(self.value))
                    if swap
                    else op(coerce(self.value), coerce(other_wrapped.value))
                ),
                callback=aggregate_callbacks([self.callback, other_wrapped.callback]),
            )
        except (TypeError, ValueError):
            return Expr(None)

    # Comparison operators
    def __eq__(self, other: any) -> "Expr":
        return self.__wrap_binary_op(other, operator.eq)

    def __ne__(self, other: any) -> "Expr":
        return self.__wrap_binary_op(other, operator.ne)

    def __lt__(self, other: any) -> "Expr":
        return self.__wrap_binary_op(other, operator.lt, float)

    def __le__(self, other: any) -> "Expr":
        return self.__wrap_binary_op(other, operator.le, float)

    def __gt__(self, other: any) -> "Expr":
        return self.__wrap_binary_op(other, operator.gt, float)

    def __ge__(self, other: any) -> "Expr":
        return self.__wrap_binary_op(other, operator.ge, float)

    # Arithmetic operators
    def __pos__(self) -> "Expr":
        try:
            self.value = +self.value
            return self
        except TypeError:
            return Expr(None)

    def __neg__(self) -> "Expr":
        try:
            self.value = -self.value
            return self
        except TypeError:
            return Expr(None)

    def __add__(self, other: any) -> "Expr":
        return self.__wrap_binary_op(other, operator.add, float)

    def __radd__(self, other: any) -> "Expr":
        return self.__wrap_binary_op(other, operator.add, float, True)

    def __sub__(self, other: any) -> "Expr":
        return self.__wrap_binary_op(other, operator.sub, float)

    def __rsub__(self, other: any) -> "Expr":
        return self.__wrap_binary_op(other, operator.sub, float, True)

    def __mul__(self, other: any) -> "Expr":
        return self.__wrap_binary_op(other, operator.mul, float)

    def __rmul__(self, other: any) -> "Expr":
        return self.__wrap_binary_op(other, operator.mul, float, True)

    def __truediv__(self, other: any) -> "Expr":
        return self.__wrap_binary_op(other, operator.truediv, float)

    def __rtruediv__(self, other: any) -> "Expr":
        return self.__wrap_binary_op(other, operator.truediv, float, True)

    def __bool__(self):
        raise Exception(
            """
            It is intentional that you cannot convert an Expr to a boolean.
            
            If you're trying to use boolean operators with conditions, please use function equivalents instead:
              a and b -> and_(a, b)
              a or b -> or_(a, b)
              not a -> not_(a)
            """
        )


def aggregate_callbacks(
    callbacks: list[Callable[[dict], None]]
) -> Callable[[dict], None] | None:
    """
    Aggregates a list of callbacks into a single callback that calls all the callbacks.
    If valid callbacks are found, returns a thunk that calls all the callbacks.
    Otherwise, returns None.
    """
    valid_callbacks = [callback for callback in callbacks if callback is not None]
    if valid_callbacks:

        def thunk(ctx: dict):
            for callback in valid_callbacks:
                callback(ctx)

        return thunk
    return None
