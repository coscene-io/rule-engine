from inspect import signature, Parameter
from dataclasses import dataclass
from ruleengine.dsl.condition import Condition
from ruleengine.dsl.base_actions import (
    create_upload_action,
    create_create_moment_action,
)


@dataclass
class UnknownFunctionKeywordArgException(Exception):
    name: str


class AcionValidator:
    def __init__(self, action_impls):
        self.__impls = action_impls

    def upload(self, *args, **kwargs):
        def validate_arg_types(args):
            # TODO: Validate arg types
            pass

        return self._validate_factory_func(
            create_upload_action(self.__impls["upload"]),
            args,
            kwargs,
            validate_arg_types,
        )

    def create_moment(self, *args, **kwargs):
        def validate_arg_types(args):
            # TODO: Validate arg types
            pass

        return self._validate_factory_func(
            create_create_moment_action(self.__impls["create_moment"]),
            args,
            kwargs,
            validate_arg_types,
        )

    def _validate_factory_func(self, factory, args, kwargs, param_type_check):
        sig = signature(factory)

        # We first do a manual check of the args to ensure the correct number
        # of parameters, and the right keyword args are passed. We don't use the
        # `bind` call below because it raises a TypeError, and we can't extract
        # the failure reason to report back to the user
        self._validate_signature(sig, args, kwargs)

        param_type_check(sig.bind(*args, **kwargs).arguments)

        return factory(*args, **kwargs)

    def _validate_signature(self, sig, args, kwargs):
        for key in kwargs:
            if key not in sig.parameters:
                raise UnknownFunctionKeywordArgException(key)

        required_args = [
            1
            for name, param in sig.parameters.items()
            if name not in kwargs and param.default is Parameter.empty
        ]
        if len(required_args) != len(args):
            # TODO: Make this an actual error instead of a generic error
            raise Exception(
                f"Wrong number of parameters. Expected {len(required_args)} but got {len(args)}"
            )
