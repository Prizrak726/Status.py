from Models.Base import *
from Models.Users import Users
from Models.Type import Type
from Models.Ticket import Ticket


class Comment(BaseModel):
    id = PrimaryKeyField(primary_key=True)
    description = TextField()
    user_id = ForeignKeyField(model=Users)
    ticket_id = ForeignKeyField(model=Ticket)
    type_id = ForeignKeyField(model=Type, default=Type.PUBLIC)