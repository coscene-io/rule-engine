from abc import ABC, abstractmethod

class Action(ABC):
    @abstractmethod
    def run(self, item, scope):
        pass


class PrintAction(Action):
    def __init__(self, target_dir, title, description):
        self.target_dir = target_dir
        self.title = title
        self.description = description

    def run(self, item, scope):
        json_object = {
            "title": self.title,
            "description": self.description,
            "timestamp": item.ts,
            "fileList": [item.topic]
        }
        with open(os.path.join(self.target_dir, str(uuid.uuid4()) + ".json"), "w") as f:
            print(f"==> Creating a moment: {self.title}")
            json.dump(json_object, f)


def create_moment(title, description):
    return PrintAction("/root/.ros/auto-upload", title, description)
