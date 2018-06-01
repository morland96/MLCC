from mongoengine import Document, IntField, ReferenceField, CASCADE, Q, StringField, DateTimeField
from .Node import Node
from datetime import datetime
from .User import User


class Work(Document):
    batch_size = IntField()
    work_name = StringField()
    details = StringField()
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    create_time = DateTimeField()
    finished_time = DateTimeField()
    script_id = StringField()
    dataset_id = StringField()
    data_num = IntField()

    @property
    def tasks(self) -> list('Task'):
        tasks = Task.objects(work=self)
        return tasks

    @property
    def tasks_progress(self):
        progresses = {}
        for task in self.tasks:
            progresses[str(task.id)] = task.progress
        return progresses

    def new_task(self):
        task = Task()
        task.status = 0
        task.work = self
        task.save()
        return task

    def get_executing(self) -> list('Task'):
        tasks = Task.objects(Q(work=self) & Q(status__lt=2))
        return tasks

    def start(self):
        self.create_time = datetime.now()
        self.save()

    def done(self):
        self.finished_time = datetime.now()
        self.save()

    def get_dict(self):
        return {
            "uuid":
            str(self.id),
            "user":
            self.user.username,
            "work_name":
            self.work_name,
            "batch_size":
            self.batch_size,
            "details":
            self.details,
            "create_time":
            (self.create_time.isoformat() + 'Z')
            if self.create_time is not None else "",
            "finished_time": (self.finished_time.isoformat() + 'Z')
            if self.finished_time is not None else "",
            "progress":
            self.tasks_progress,
            "data_num":
            self.data_num
        }


class Task(Document):
    # status = ["Pendding", "Executing", "Done", "None", "Error"]
    work = ReferenceField(Work, reverse_delete_rule=CASCADE)
    status = IntField(required=False)
    consumer_node = ReferenceField(Node, reverse_delete_rule=CASCADE)
    progress = IntField(defualt=0)