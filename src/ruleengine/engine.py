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

import logging
from dataclasses import dataclass, field
from typing import Any

_log = logging.getLogger(__name__)


@dataclass
class DiagnosisItem:
    topic: str
    msg: Any
    ts: float
    msgtype: str


@dataclass
class Rule:
    conditions: list
    actions: list
    initial_scope: dict
    upload_limit: dict = field(default_factory=dict)
    spec: dict = field(default_factory=dict)
    project_name: str = ""


class Engine:
    def __init__(self, rules, should_trigger_action=None, trigger_cb=None):
        self.__rules = rules
        self.__should_trigger_action = should_trigger_action
        self.__trigger_cb = trigger_cb

    def consume_next(self, item):
        for rule in self.__rules:
            triggered_condition_indices = []
            triggered_scope = None

            for i, cond in enumerate(rule.conditions):
                res, scope = cond.evaluate_condition_at(item, rule.initial_scope)
                _log.debug(f"evaluate condition, result: {res}, scope: {scope}")
                if res:
                    triggered_condition_indices.append(i)
                if not triggered_scope:
                    triggered_scope = scope

            if not triggered_condition_indices:
                continue

            # For testing, rule.spec is not specified
            hit = (
                {}
                if not rule.spec
                else {
                    **rule.spec,
                    "when": [rule.spec["when"][i] for i in triggered_condition_indices],
                }
            )

            action_triggered = False
            if not self.__should_trigger_action or self.__should_trigger_action(
                rule.project_name, rule.spec, hit
            ):
                action_triggered = True
                for action in rule.actions:
                    action.run(item, triggered_scope)

            if self.__trigger_cb:
                self.__trigger_cb(
                    rule.project_name, rule.spec, hit, action_triggered, item
                )
