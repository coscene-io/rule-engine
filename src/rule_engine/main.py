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

from rule_engine.action import noop_action_impls
from rule_engine.rule import spec_to_rules, validate_rules

if __name__ == "__main__":
    config = json.loads(argv[1])
    rules = spec_to_rules(config, noop_action_impls)
    result = validate_rules(rules)

    print(result.model_dump_json(exclude_unset=True))
    exit(0 if result["success"] else 1)
