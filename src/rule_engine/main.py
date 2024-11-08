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

import json
from sys import argv

from rule_engine.rule import (
    ALLOWED_VERSIONS as ALLOWED_VERSIONS_2,
    spec_to_rules,
    validate_rules,
)
from rule_engine.utils import (
    ValidationError,
    ValidationErrorUnexpectedVersion,
    ValidationResult,
)
from ruleengine.dsl.base_actions import noop
from ruleengine.dsl.validation.config_validator import (
    ALLOWED_VERSIONS as ALLOWED_VERSIONS_1,
    validate_config,
)

ALLOWED_VERSIONS = ALLOWED_VERSIONS_1 + ALLOWED_VERSIONS_2


def main(rule_set_spec_str: str):
    rule_set_spec = json.loads(rule_set_spec_str)

    if not rule_set_spec.get("version", "") in ALLOWED_VERSIONS:
        print(
            ValidationResult(
                success=True,
                errors=[
                    ValidationError(
                        unexpected_version=ValidationErrorUnexpectedVersion(
                            allowedVersions=ALLOWED_VERSIONS,
                        )
                    )
                ],
            ).model_dump_json(exclude_unset=True)
        )
        exit(1)

    if rule_set_spec.get("version") in ALLOWED_VERSIONS_1:
        result, _ = validate_config(rule_set_spec, noop)
        print(json.dumps(result))
        exit(0 if result["success"] else 1)

    if rule_set_spec.get("version") in ALLOWED_VERSIONS_2:
        rules = spec_to_rules(rule_set_spec, {})
        result = validate_rules(rules)
        print(result.model_dump(exclude_unset=True))
        exit(0 if result.success else 1)


if __name__ == "__main__":
    main(argv[1])
