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

from enum import Enum

from .base_conditions import and_, msg, msgtype, or_
from .condition import Condition

# TODO: Add tests
# TODO: Add other fields that are common for logs

_is_foxglove = or_(msgtype == "foxglove_msgs/Log", msgtype == "foxglove.Log")
_is_ros = msgtype == "rosgraph_msgs/Log"

LogLevel = Enum("LogLevel", ["UNKNOWN", "DEBUG", "INFO", "WARN", "ERROR", "FATAL"])

log = or_(
    and_(_is_ros, msg.msg),
    and_(_is_foxglove, msg.message),
    # Default case
    "",
)

log_level = or_(
    and_(_is_ros, Condition.map(msg, lambda m: ros_log_level(m.level))),
    and_(_is_foxglove, Condition.map(msg, lambda m: foxglove_log_level(m.level))),
    # Default case
    LogLevel.UNKNOWN,
)


def ros_log_level(num):
    if num == 1:
        return LogLevel.DEBUG
    elif num == 2:
        return LogLevel.INFO
    elif num == 4:
        return LogLevel.WARN
    elif num == 8:
        return LogLevel.ERR
    elif num == 16:
        return LogLevel.FATAL
    else:
        return LogLevel.UNKNOWN


def foxglove_log_level(num):
    if num == 1:
        return LogLevel.DEBUG
    elif num == 2:
        return LogLevel.INFO
    elif num == 3:
        return LogLevel.WARN
    elif num == 4:
        return LogLevel.ERROR
    elif num == 5:
        return LogLevel.FATAL
    else:
        return LogLevel.UNKNOWN


__all__ = [
    "log",
    "log_level",
    "LogLevel",
]
