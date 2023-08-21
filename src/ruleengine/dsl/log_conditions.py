from enum import Enum

from .base_conditions import and_, msg, or_, type_is

# TODO: Add tests
# TODO: Add other fields that are common for logs

_is_foxglove = or_(type_is("foxglove_msgs/Log"), type_is("foxglove.Log"))
_is_ros = type_is("rosgraph_msgs/Log")

LogLevel = Enum("LogLevel", ["UNKNOWN", "DEBUG", "INFO", "WARN", "ERROR", "FATAL"])

log_text = or_(
    and_(_is_ros, msg.msg),
    and_(_is_foxglove, msg.message),
    # Default case
    "",
)

log_level = or_(
    and_(_is_ros, msg.map_condition_value(lambda m: ros_log_level(m.level))),
    and_(_is_foxglove, msg.map_condition_value(lambda m: foxglove_log_level(m.level))),
    # Default case
    LogLevel.UNKNOWN,
)


def ros_log_level(num):
    match num:
        case 1:
            return LogLevel.DEBUG
        case 2:
            return LogLevel.INFO
        case 4:
            return LogLevel.WARN
        case 8:
            return LogLevel.ERROR
        case 16:
            return LogLevel.FATAL
        case _:
            return LogLevel.UNKNOWN


def foxglove_log_level(num):
    match num:
        case 1:
            return LogLevel.DEBUG
        case 2:
            return LogLevel.INFO
        case 3:
            return LogLevel.WARN
        case 4:
            return LogLevel.ERROR
        case 5:
            return LogLevel.FATAL
        case _:
            return LogLevel.UNKNOWN


__all__ = [
    "log_text",
    "log_level",
    "LogLevel",
]
