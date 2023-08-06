import os.path
import sys
import json
import uuid
from ruleengine.engine import Engine, Rule
from ruleengine.dsl.actions import Action
from ruleengine.dsl.base_conditions import msg
import tailer


class PrintAction(Action):
    def __init__(self, target_dir):
        self.target_dir = target_dir

    def run(self, item, scope):
        json_object = {
            "title": "Found error code",
            "description": "Found error code description",
            "timestamp": int(item.ts.timestamp()),
            "files": [item.topic]
        }
        with open(os.path.join(self.target_dir, str(uuid.uuid4()) + ".json"), "w") as f:
            json.dump(json_object, f)

def main():
    watch_log_dir = sys.argv[1]
    target_dir = sys.argv[2]
    # rules = [Rule(msg.map_condition_value(lambda x: "Link encap:UNSPEC  HWaddr" in x), PrintAction())]
    rules = [Rule(msg("Link encap:UNSPEC  HWaddr"), PrintAction(target_dir))]
    Engine(rules, tailer.tail_lines_from_dir(watch_log_dir)).run()


if __name__ == '__main__':
    main()
