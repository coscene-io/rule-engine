import inspect
from ruleengine import dsl

base_dsl_values = dict(inspect.getmembers(dsl))

def upload(
    before=10,
    title="",
    description="",
    labels=[],
    extra_files=[],
):
    pass

def create_moment(
    title,
    description="",
    timestamp=0,
    duration=1,
    create_task=False,
    assign_to=None,
):
    pass

actions_dsl_values = {
        'upload': upload,
        'create_moment': create_moment,
        **base_dsl_values
        }

def validate_condition(cond_str):
    eval(cond_str, base_dsl_values)

def validate_action(action_str):
    eval(action_str, actions_dsl_values)

