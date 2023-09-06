from .dsl.action import Action
from .dsl.condition import Condition

# TODO: Rule and Engine classes are deprecated, remove the code after cleaning
# up call sites. New code should use `run` below.


class Rule:
    def __init__(self, condition, action):
        assert isinstance(condition, Condition)
        assert isinstance(action, Action)

        self.__cond = condition
        self.__action = action

    def eval_condition(self, item):
        return self.__cond.evaluate_condition_at(item, {})

    def run_action(self, item, scope):
        return self.__action.run(item, scope)


class Engine:
    def __init__(self, rules, data):
        self.__rules = rules
        self.__data = data

    def run(self):
        for item in self.__data:
            for rule in self.__rules:
                result, scope = rule.eval_condition(item)
                if result:
                    rule.run_action(item, scope)


class Engine2:
    def __init__(self, rules):
        self.__rules = rules

    def consume_next(self, item):
        for conditions, actions in self.__rules:
            for cond in conditions:
                res, scope = cond.evaluate_condition_at(item, {})
                if res:
                    for action in actions:
                        action.run(item, scope)
                    break
