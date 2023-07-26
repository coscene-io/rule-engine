from abc import ABC, abstractmethod

class Action(ABC):
    @abstractmethod
    def run(self, data):
        pass

class PrintAction(Action):
    def __init__(self, items):
        self.__items = items

    def run(self, data):
        for i in self.__items:
            print(i.evaluate_condition_at(data))

def print_to_console(*args):
    return PrintAction(args)
