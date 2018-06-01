from mongoengine import Document, StringField, FloatField, IntField, ListField


class Node(Document):
    hostname = StringField(required=True)
    cpu_usage = FloatField()
    cpu_freq = IntField()
    cpu_usage_history = ListField(FloatField())

    def get_dict(self):
        return {
            'hostname': self.hostname,
            'cpu_usage': self.cpu_usage,
            'cpu_freq': self.cpu_freq,
            'cpu_usage_history': self.cpu_usage_history
        }
