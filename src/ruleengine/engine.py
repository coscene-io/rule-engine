from .dsl.condition import Condition
from .dsl.actions import Action

class Rule:
    def __init__(self, condition, action):
        assert isinstance(condition, Condition)
        assert isinstance(action, Action)

        self.__cond = condition
        self.__action = action

    def eval_condition(self, item):
        scope = {}
        return self.__cond.evaluate_condition_at(item, scope), scope

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

