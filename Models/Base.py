from peewee import Model
from Connect.connect import connect

class BaseModel(Model):
    class Meta:
        database = connect()