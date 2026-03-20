from Models.Base import *
from peewee import *

class Status(BaseModel):
    # Фиксированные статусы заявки
    NEW = 1
    IN_PROGRESS = 2
    RESOLVED = 3
    CLOSED = 4

    id = PrimaryKeyField(primary_key=True)
    name = CharField(unique=True)

    class Meta:
        table_name = "status"