import cProfile
from sys import argv

from ruleengine.dsl.validation.config_validator import validate_config
from ruleengine.engine import Engine, DiagnosisItem

SAMPLE_CONFIG = {
    "version": "v1",
    "rules": [
        {
            "when": [
                '"error 1" in msg',
                '"error 21444444" in msg or "asioehtnai" in msg or "aioentaihe" in msg',
                '"error 21444444" in msg or "asioehtnai" in msg or "aioentaihe" in msg',
                '"error 21444444" in msg or "asioehtnai" in msg or "aioentaihe" in msg',
                '"error 21444444" in msg or "asioehtnai" in msg or "aioentaihe" in msg',
            ],
            "actions": ["upload()"],
        }
    ],
}


def sample_action(*args, **kwargs):
    print(args, kwargs)


if __name__ == "__main__":
    res, rules = validate_config(
        SAMPLE_CONFIG, {"upload": sample_action, "create_moment": sample_action}
    )
    assert res["success"], res
    engine = Engine(rules)

    with open(argv[1]) as f:
        lines = [
            DiagnosisItem(topic=argv[1], msg=line, ts=0, msgtype="log") for line in f
        ]

    def go():
        for item in lines:
            engine.consume_next(item)

    cProfile.run("go()")
