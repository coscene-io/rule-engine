from .dsl.condition import Condition

class Rule:
    def __init__(self, condition, action):
        assert isinstance(condition, Condition)
        # TODO: Check action class

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
        pass


