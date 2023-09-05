from ruleengine.dsl.condition import Condition
from ruleengine.dsl.action import Action
from typing import Optional


def noop_upload(
    before: int, title: str, description: str, labels: list[str], extra_files: list[str]
):
    pass


def noop_create_moment(
    title: str,
    description: str,
    timestamp: int,
    duration: int,
    create_task: bool,
    assign_to: Optional[str],
):
    pass

noop = {"upload": noop_upload, "create_moment": noop_create_moment}

class ForwardingAction(Action):
    def __init__(self, thunk, args):
        self.__thunk = thunk
        self.__args = args

    def run(self, item, scope):
        actual_args = {}
        for name, value in self.__args.items():
            if isinstance(value, Condition):
                new_value, _ = value.evaluate_condition_at(item, scope)
                actual_args[name] = new_value
            else:
                actual_args[name] = value
        self.__thunk(**actual_args)
