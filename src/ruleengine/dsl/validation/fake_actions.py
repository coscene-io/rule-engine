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


action_dict = {
        "upload": upload,
        "create_moment" : create_moment
}


__all__ = [
    "action_dict",
]
