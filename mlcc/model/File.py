from mongoengine import Document, StringField, ReferenceField, CASCADE, DateTimeField
from .User import User
from datetime import datetime
time_format = '%Y-%m-%dT%H:%M:%S.%f'


class File(Document):
    filename = StringField()
    uploader = ReferenceField(User, reverse_delete_rule=CASCADE)
    details = StringField()
    upload_time = DateTimeField(default=datetime.now(), required=True)

    def get_dict(self):
        return {
            "uuid": str(self.id),
            "filename": self.filename,
            "uploader": self.uploader.username,
            "details": self.details,
            "upload_time": self.upload_time.isoformat() + 'Z'
        }


class Script(Document):
    script_name = StringField()
    uploader = ReferenceField(User, reverse_delete_rule=CASCADE)
    details = StringField()
    upload_time = DateTimeField(default=datetime.now(), required=True)
    language = StringField()

    def get_dict(self):
        return {
            "uuid": str(self.id),
            "script_name": self.script_name,
            "language": self.language,
            "uploader": self.uploader.username,
            "details": self.details,
            "upload_time": self.upload_time.isoformat() + 'Z'
        }
