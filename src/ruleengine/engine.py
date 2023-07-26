from .dsl.condition import Condition
from .dsl.actions import Action

class Rule:
    def __init__(self, condition, action):
        assert isinstance(condition, Condition)
        assert isinstance(action, Action)

        self.__cond = condition
        self.__action = action

    def eval_condition(self, item):
        return self.__cond(item)

    def run_action(self, item):
        return self.__action(item)


class Engine:
    def __init__(self, rules, data):
        self.__rules = rules
        self.__data = data

    def run(self):
        for item in self.__data:
            for rule in self.__rules:
                if rule.eval_condition(item):
                    rule.run_action(item)

