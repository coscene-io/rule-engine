from ruleengine.dsl.condition import Condition
from ruleengine.dsl.base_conditions import ts
from ruleengine.dsl.base_actions import ForwardingAction, noop_upload, noop_create_moment

class AcionValidator:
    def __init__(self, action_impls):
        self.__impls = action_impls

    def create_upload_action(self, before, title, description, labels=[], extra_files=[]):
        # TODO: Validate arg types

        args = {
                'before': before,
                'title': Condition.wrap(title),
                'description': Condition.wrap(description),
                'labels': labels,
                'extra_files': extra_files
                }

        return ForwardingAction(self.__impls['upload'], args)

    def create_create_moment_action(self, title, description='', timestamp=ts, duration=1, create_task=False, assign_to=None):
        # TODO: Validate arg types

        args = {
                'title': Condition.wrap(title),
                'description': Condition.wrap(description),
                'timestamp': timestamp,
                'duration': Condition.wrap(duration),
                'create_task': create_task,
                'assign_to': assign_to
                }
        return ForwardingAction(self.__impls['create_moment'], args)

noop = AcionValidator({ 'upload': noop_upload, 'create_moment': noop_create_moment})
