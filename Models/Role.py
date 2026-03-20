from peewee import *
from Models.Base import BaseModel

class Role(BaseModel):
    USER = 1
    SPECIALIST = 2
    ADMIN = 3

    id = PrimaryKeyField(primary_key=True)
    name = CharField(unique=True)

    class Meta:
        table_name = "role"