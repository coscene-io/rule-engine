from ruleengine.dsl.base_conditions import *
from ruleengine.dsl.sequence_conditions import *
from ruleengine.dsl.log_conditions import *

def validate_condition(cond_str):
    eval(cond_str)


def validate_action(action_str):
    def upload(
        before = 10,
        title = '',
        description = '',
        labels = [],
        extra_files = [],
    ):
        pass

    def create_moment(
        title,
        description = '',
        timestamp = 0,
        duration = 1,
        create_task = False,
        assign_to = None,
    ):
        pass

    eval(action_str)
