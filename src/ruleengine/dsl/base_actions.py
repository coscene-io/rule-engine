from ruleengine.dsl.condition import Condition
from ruleengine.dsl.base_conditions import ts, concat
from ruleengine.dsl.action import Action
from typing import Optional


def noop_upload(
    trigger_ts: int,
    before: int,
    title: str,
    description: str,
    labels: list[str],
    extra_files: list[str],
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


def upload_factory(impl):
    def res(
        title=concat("Device auto upload @ ", ts),
        description="",
        labels=[],
        extra_files=[],
        before=10,
    ):
        args = {
            "before": before,
            "title": Condition.map(Condition.wrap(title), str),
            "description": Condition.map(Condition.wrap(description), str),
            "labels": labels,
            "extra_files": extra_files,
            "trigger_ts": ts,
        }

        return ForwardingAction(impl, args)

    return res


def create_moment_factory(impl):
    def res(
        title,
        description="",
        timestamp=ts,
        duration=1,
        create_task=False,
        assign_to=None,
    ):
        args = {
            "title": Condition.map(Condition.wrap(title), str),
            "description": Condition.map(Condition.wrap(description), str),
            "timestamp": Condition.map(Condition.wrap(timestamp), int),
            "duration": Condition.map(Condition.wrap(duration), int),
            "create_task": Condition.wrap(create_task),
            "assign_to": assign_to,
        }
        return ForwardingAction(impl, args)

    return res
