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

import celpy

from rule_engine.rule import Rule


class Engine:
    """
    The rule engine represents a collection of rules
    """

    def __init__(self, rules: list[Rule]):
        self.rules = rules
        self.cur_activation = None

    def example_consume_next(self, msg: dict[str, any], topic: str, ts: float):
        """
        An example of how to consume a message and trigger rules
        In a real-world scenario, there might be more complex logic before condition evaluation
        before action running, or after action running. Use this as a reference.
        """
        self.load_message(msg, topic, ts)
        for rule_idx, _ in enumerate(self.rules):
            if self.evaluate_rule_condition(rule_idx):
                self.run_rule_actions(rule_idx)

    def load_message(self, msg: dict[str, any], topic: str, ts: float):
        """Load the message into the engine and prepared for rule evaluation"""
        self.cur_activation = {
            "msg": celpy.adapter.json_to_cel(msg),
            "topic": celpy.celtypes.StringType(topic),
            "ts": celpy.celtypes.DoubleType(ts),
        }

    def evaluate_rule_condition(self, rule_idx):
        """Evaluate the condition of a rule against the current activation"""
        rule = self.rules[rule_idx]
        activation = {
            **self.cur_activation,
            "scope": rule.scope,
        }
        return all(cond.evaluate(activation) for cond in rule.conditions)

    def run_rule_actions(self, rule_idx):
        """Run the actions of a rule against the current activation"""
        rule = self.rules[rule_idx]
        activation = {
            **self.cur_activation,
            "scope": rule.scope,
        }
        for action in rule.actions:
            action.run(activation)
