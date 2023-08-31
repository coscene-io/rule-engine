from ruleengine.dsl.action import Action


class NullAction(Action):
    def run(self, item, scope):
        pass


def upload(
    before=10,
    title="",
    description="",
    labels=[],
    extra_files=[],
):
    return NullAction()


def create_moment(
    title,
    description="",
    timestamp=0,
    duration=1,
    create_task=False,
    assign_to=None,
):
    return NullAction()


__all__ = [
    "upload",
    "create_moment",
]
