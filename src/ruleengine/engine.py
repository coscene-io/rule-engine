from .dsl.validation.validator import validate_condition, validate_action
from .dsl.action import Action
from .dsl.condition import Condition


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


def run(rule_configs, action_impl, data):
    """
    TODO: write this
    """

    rules = []
    for c in rule_configs:
        conditions = [validate_condition(cond_str) for cond_str in c['when']]
        actions = [validate_action(action_str) for action_str in c['actions']]
        rules.append((conditions, actions))

    for item in self.__data:
        for conditions, actions in rules:
            for cond in conditions:
                res, scope = cond.evaluate_condition_at(item, {})
                if res:
                    for action in actions:
                        action.run(item, scope)
                    break

