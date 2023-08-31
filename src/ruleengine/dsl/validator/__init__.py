import json

from .core import eval_action, eval_condition, validate_action as validate_action_inner, validate_condition as validate_condition_inner

def validate_action(action_str, structured_output):
    if structured_output:
        return validate_action_inner(action_str)
    eval_action(action_str)

def validate_condition(cond_str, structured_output):
    if structured_output:
        return validate_condition_inner(cond_str)
    eval_condition(cond_str)

__all__ = [
        'validate_action',
        'validate_condition'
        ]

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate condition or action strings")
    parser.add_argument(
        "mode",
        help="What we're validating, action or condition",
        choices=["action", "condition"],
    )
    parser.add_argument("content", help="Content string to be validated")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    match args.mode:
        case "action":
            result = validate_action(args.content, args.json)
        case "condition":
            result = validate_condition(args.content, args.json)
        case _:
            pass

    if args.json:
        print(json.dumps(result.asdict()))

