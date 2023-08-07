#!/usr/bin/env python3

import sys
from ruleengine.engine import Engine, Rule
from rules import rules
import tailer

def main():
    watch_log_dir = sys.argv[1]
    Engine(rules, tailer.tail_lines_from_dir(watch_log_dir)).run()


if __name__ == '__main__':
    main()
