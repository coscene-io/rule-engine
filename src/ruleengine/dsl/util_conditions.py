from .base_conditions import *

log_text = or_(
    and_(type_is('foxglove_msgs/Log'), msg.message),
    and_(type_is('foxglove.Log'), msg.message),
    and_(type_is('rosgraph_msgs/Log'), msg.msg),
)

