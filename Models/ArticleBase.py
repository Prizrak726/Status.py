from peewee import *
from Models.Base import *
from Models.Ticket import Ticket
from Models.Users import Users


class ArticleBase(BaseModel):
    id = PrimaryKeyField(primary_key=True)
    title = TextField()
    description = TextField()
    ticket_id = ForeignKeyField(model=Ticket)
    executor_id = ForeignKeyField(model=Users)