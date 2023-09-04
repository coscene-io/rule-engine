# TODO: This validator was written in a rush. It has a number of issues, and is
# now deprecated. After switching over to the `ruleengine.dsl.validation`
# package, we should remove this file.

import inspect
from ruleengine.dsl import base_conditions, log_conditions, sequence_conditions


base_dsl_values = dict(
    inspect.getmembers(base_conditions)
    + inspect.getmembers(log_conditions)
    + inspect.getmembers(sequence_conditions)
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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate condition or action strings")
    parser.add_argument(
        "mode",
        help="What we're validating, action or condition",
        choices=["action", "condition"],
    )
    parser.add_argument("content", help="Content string to be validated")
    args = parser.parse_args()

    match args.mode:
        case "action":
            validate_action(args.content)
        case "condition":
            validate_condition(args.content)
