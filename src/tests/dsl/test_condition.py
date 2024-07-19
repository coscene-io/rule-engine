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

import unittest

from ruleengine.dsl.condition import Condition


class ConditionTest(unittest.TestCase):
    def test_arithmetics(self):
        self.assertEqual(-4, int(self._get_eval_result(-Condition.wrap(4))))
        self.assertEqual(4, int(self._get_eval_result(+Condition.wrap(4))))

        self.assertEqual(10, int(self._get_eval_result(Condition.wrap(4) + 6)))
        self.assertEqual(10, int(self._get_eval_result(6 + Condition.wrap(4))))

        self.assertEqual(-2, int(self._get_eval_result(Condition.wrap(4) - 6)))
        self.assertEqual(2, int(self._get_eval_result(6 - Condition.wrap(4))))

        self.assertEqual(24, int(self._get_eval_result(Condition.wrap(4) * 6)))
        self.assertEqual(24, int(self._get_eval_result(6 * Condition.wrap(4))))

        self.assertEqual(2, int(self._get_eval_result(Condition.wrap(12) / 6)))
        self.assertEqual(2, int(self._get_eval_result(12 / Condition.wrap(6))))

    def _get_eval_result(self, cond):
        return cond.evaluate_condition_at(None, {})[0]
