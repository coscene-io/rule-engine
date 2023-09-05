from ruleengine.dsl.condition import Condition
from ruleengine.dsl.base_actions import create_upload_action, create_create_moment_action


class AcionValidator:
    def __init__(self, action_impls):
        self.__impls = action_impls

    def upload( self, *args, **kwargs):
        # TODO: Validate arg types
        return create_upload_action(self.__impls["upload"], *args, **kwargs)

    def create_moment( self, *args, **kwargs):
        # TODO: Validate arg types
        return create_create_moment_action(self.__impls["create_moment"], *args, **kwargs)

