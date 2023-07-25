from coscene.engine import Engine, RuleSet
from coscene.dsl import *

# Assumed imports from dsl package, used in the following rules:
#   topic, msg, ts, evaluate, seq, seconds, kv, set_val, get_val, create_moment

rules = RuleSet()

rules.add_rule(
    topic('/device/status') and 'HUB disconnect' in msg.data,
    create_moment('hub disconnect', ts))

rules.add_rule(
    topic('/checker/warning_event'),
    create_moment(evaluate(msg, lambda m: ERROR_CODES.get(str(m.error_code))), ts))

rules.add_rule(
    seq(
        topic('rosout') and 'task/pause' in msg.msg,
        topic('rosout') and 'start_cross_task' in msg.msg,
        within=seconds(10)),
    create_moment('异常停车：机器执行任务中被人为暂停，然后点击了回家'))

charger_voltage = float(kv(msg.values)['charger_voltage'])
charger_current = float(kv(msg.values)['charger_current'])
rules.add_rule(
    not seq(
        topic('device_status') and charger_voltage > 0.0 and charger_current == 0,
        topic('device_status') and charger_current > 0.0 and charger_current > 0,
        within=seconds(20)),
    create_moment('对桩失败问题：机器对桩后不充电 (等了20秒)'))

rules.add_rule(
    seq(
        topic('request') and set_val('req_id', msg.id),
        topic('reponse') and msg.req_id == get_val('req_id'),
        within=seconds(10)),
    create_moment('Did not get a response within 10 seconds'))

Engine().run(rules, bag)
