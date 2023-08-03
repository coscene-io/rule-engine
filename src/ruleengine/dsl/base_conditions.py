from .condition import PointCondition

always = PointCondition.wrap(True)
msg = PointCondition().map_condition_value(lambda x: x.msg)
ts = PointCondition().map_condition_value(lambda x: x.ts)
topic = PointCondition().map_condition_value(lambda x: x.topic)

def get_value(key):
    return PointCondition.wrap(key).map_condition_value(
            lambda key: PointCondition(lambda item, scope: (scope[key], {})))

def set_value(key, value):
    return PointCondition.wrap(key).map_condition_value(
        lambda actual_key: PointCondition.wrap(value).map_condition_value(
            lambda actual_value: PointCondition(
                lambda item, scope: (True, { actual_key: actual_value }))))

def topic_is(name):
    return topic.map_condition_value(lambda t: t == name)

def type_is(name):
    return msg.map_condition_value(lambda m: type(m).__name__ == name)

