from ruleengine.dsl.condition import Condition
from ruleengine.dsl.base_conditions import ts, concat
from ruleengine.dsl.base_actions import ForwardingAction


class AcionValidator:
    def __init__(self, action_impls):
        self.__impls = action_impls

    # TODO: It's weird that default values are specified in the validator
    # instead of action implementation proper.
    def create_upload_action(
        self,
        title=concat("Device auto upload @ ", ts),
        description="",
        labels=[],
        extra_files=[],
        before=10,
    ):
        # TODO: Validate arg types

        args = {
            "before": before,
            "title": Condition.wrap(title),
            "description": Condition.wrap(description),
            "labels": labels,
            "extra_files": extra_files,
        }

        return ForwardingAction(self.__impls["upload"], args)

    # TODO: It's weird that default values are specified in the validator
    # instead of action implementation proper.
    def create_create_moment_action(
        self,
        title,
        description="",
        timestamp=ts,
        duration=1,
        create_task=False,
        assign_to=None,
    ):
        # TODO: Validate arg types

        args = {
            "title": Condition.wrap(title),
            "description": Condition.wrap(description),
            "timestamp": Condition.wrap(timestamp),
            "duration": Condition.wrap(duration),
            "create_task": create_task,
            "assign_to": assign_to,
        }
        return ForwardingAction(self.__impls["create_moment"], args)
