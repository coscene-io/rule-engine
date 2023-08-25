import inspect
from ruleengine.dsl import base_conditions, log_conditions, sequence_conditions

base_dsl_values = dict(
        inspect.getmembers(base_conditions) +
        inspect.getmembers(log_conditions) +
        inspect.getmembers(sequence_conditions)
        )


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
    "upload": upload,
    "create_moment": create_moment,
    **base_dsl_values,
}


def validate_condition(cond_str):
    # TODO: Very much not safe. Condition strings are user supplied, and we need
    # to sanitize the fuck out of it before doing eval.
    return eval(cond_str, base_dsl_values)


def validate_action(action_str):
    # TODO: Very much not safe. Condition strings are user supplied, and we need
    # to sanitize the fuck out of it before doing eval.
    return eval(action_str, actions_dsl_values)
