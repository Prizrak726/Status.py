
from datetime import datetime

from Models.Base import *
from Models.Category import Category
from Models.Status import Status
from Models.Users import Users


class Ticket(BaseModel):
    id = PrimaryKeyField(primary_key=True)
    title = CharField()
    description = TextField()
    status_id = ForeignKeyField(model=Status)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    user_id = ForeignKeyField(model=Users)
    executor_id = ForeignKeyField(model=Users, null=True)
    category_id = ForeignKeyField(model=Category)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)