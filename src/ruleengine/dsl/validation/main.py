import json
from dataclasses import asdict
from ruleengine.dsl.validation.validator import validate_action, validate_condition

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
            result = validate_action(args.content)
        case "condition":
            result = validate_condition(args.content)

    print(json.dumps(asdict(result)))
    exit(0 if result.success else 1)
