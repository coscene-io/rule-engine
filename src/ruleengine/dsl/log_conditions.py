from .base_conditions import *

# TODO: Add tests
# TODO: Add other fields that are common for logs

_is_foxglove = or_(type_is('foxglove_msgs/Log'), type_is('foxglove.Log'))
_is_ros = type_is('rosgraph_msgs/Log')

log_text = or_(
    and_(_is_ros, msg.msg),
    and_(_is_foxglove, msg.message),

    # Default case
    '',
)

log_level = or_(
    and_(_is_ros, msg.map_condition_value(lambda m: ros_log_level(m.level))),
    and_(_is_foxglove, msg.map_condition_value(lambda m: foxglove_log_level(m.level))),

    # Default case
    'UNKNOWN',
)

def ros_log_level(num):
    match num:
        case 1: return 'DEBUG'
        case 2: return 'INFO'
        case 4: return 'WARN'
        case 8: return 'ERROR'
        case 16: return 'FATAL'
        _: return 'UNKNOWN'


def foxglove_log_level(num):
    match num:
        case 1: return 'DEBUG'
        case 2: return 'INFO'
        case 3: return 'WARN'
        case 4: return 'ERROR'
        case 5: return 'FATAL'
        _: return 'UNKNOWN'

