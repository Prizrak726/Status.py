from Models.Base import *

class Type(BaseModel):
    PUBLIC = 1      # Видно всем (пользователь, тех, админ)
    INTERNAL = 2    # Внутренний, только тех + админ

    id = PrimaryKeyField(primary_key=True)
    name = CharField(unique=True)

    class Meta:
        table_name = "type"