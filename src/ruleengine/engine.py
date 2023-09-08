class Engine:
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
