from .condition import PointCondition, evaluate

msg = PointCondition(lambda x: x.msg)
ts = PointCondition(lambda x: x.ts)
topic = PointCondition(lambda x: x.topic)

def topic_is(name):
    return topic.map_condition_value(lambda t: t == name)

def type_is(name):
    return msg.map_condition_value(lambda m: type(m).__name__ == name)

