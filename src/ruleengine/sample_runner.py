# Copyright 2024 coScene
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import cProfile
from sys import argv

from ruleengine.dsl.validation.config_validator import validate_config
from ruleengine.engine import DiagnosisItem, Engine

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
