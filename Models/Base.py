from Connect.connect import *

class BaseModel(Model):
    class Meta:
        database = connect()