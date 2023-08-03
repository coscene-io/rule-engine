from .condition import Condition, ThunkCondition

always = Condition.wrap(True)
identity = ThunkCondition(lambda item, scope: (item, scope))
msg = identity.map_condition_value(lambda x: x.msg)
ts = identity.map_condition_value(lambda x: x.ts)
topic = identity.map_condition_value(lambda x: x.topic)

def get_value(key):
    return Condition.wrap(key).map_condition_value(
            lambda key: ThunkCondition(lambda item, scope: (scope[key], scope)))

def set_value(key, value):
    return Condition.wrap(key).map_condition_value(
        lambda actual_key: Condition.wrap(value).map_condition_value(
            lambda actual_value: ThunkCondition(
                lambda item, scope: (True, { **scope, actual_key: actual_value }))))

def topic_is(name):
    return topic.map_condition_value(lambda t: t == name)

def type_is(name):
    return msg.map_condition_value(lambda m: type(m).__name__ == name)

