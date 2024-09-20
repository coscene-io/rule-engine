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

from typing import List, Optional

from ruleengine.dsl.action import Action
from ruleengine.dsl.base_conditions import concat, condition_start_time, ts
from ruleengine.dsl.condition import Condition


def noop_upload(
    trigger_ts: int,
    before: int,
    after: int,
    title: str,
    description: str,
    labels: List[str],
    extra_files: List[str],
    white_list: List[str],
):
    pass


def noop_create_moment(
    title: str,
    description: str,
    timestamp: int,
    start_time: int,
    create_task: bool,
    sync_task: bool,
    assign_to: Optional[str],
    custom_fields: Optional[str],
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
        white_list=[],
        before=10,
        after=0,
    ):
        args = {
            "before": before,
            "after": after,
            "title": Condition.map(Condition.wrap(title), str),
            "description": Condition.map(Condition.wrap(description), str),
            "labels": labels,
            "extra_files": extra_files,
            "white_list": white_list,
            "trigger_ts": ts,
        }

        return ForwardingAction(impl, args)

    return res


def create_moment_factory(impl):
    def res(
        title,
        description="",
        timestamp=ts,
        start_time=condition_start_time,
        create_task=False,
        sync_task=False,
        assign_to=None,
        custom_fields="",
    ):
        args = {
            "title": Condition.map(Condition.wrap(title), str),
            "description": Condition.map(Condition.wrap(description), str),
            "timestamp": Condition.map(Condition.wrap(timestamp), float),
            "start_time": Condition.map(Condition.wrap(start_time), float),
            "create_task": Condition.wrap(create_task),
            "sync_task": Condition.wrap(sync_task),
            "assign_to": assign_to,
            "custom_fields": Condition.map(Condition.wrap(custom_fields), str),
        }
        return ForwardingAction(impl, args)

    return res
