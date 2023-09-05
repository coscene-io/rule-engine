import inspect
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
        self._validate_signature(inspect.signature(create_upload_action), args, kwargs)
        # TODO: Validate arg types
        return create_upload_action(self.__impls["upload"], *args, **kwargs)

    def create_moment(self, *args, **kwargs):
        self._validate_signature(inspect.signature(create_create_moment_action), args, kwargs)
        # TODO: Validate arg types
        return create_create_moment_action(
            self.__impls["create_moment"], *args, **kwargs
        )

    def _validate_signature(self, signature, args, kwargs):
        for key in kwargs:
            if key not in signature.parameters:
                raise UnknownFunctionKeywordArgException(key)

