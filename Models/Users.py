from  Models.Base import *
from Models.Role import Role


class Users(BaseModel):
    id = PrimaryKeyField(primary_key=True)
    name = CharField()
    role = ForeignKeyField(model=Role)
    login = CharField(unique=True)
    password = CharField()
