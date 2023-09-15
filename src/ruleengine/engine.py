from dataclasses import dataclass
from typing import Any


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


class Engine:
    def __init__(self, rules):
        self.__rules = rules

    def consume_next(self, item):
        for rule in self.__rules:
            for cond in rule.conditions:
                res, scope = cond.evaluate_condition_at(item, rule.initial_scope)
                if res:
                    for action in rule.actions:
                        action.run(item, scope)
                    break
