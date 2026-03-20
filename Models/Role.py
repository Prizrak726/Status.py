from Models.Base import *


class Role(BaseModel):
    # Фиксированные идентификаторы ролей
    USER = 1          # Пользователь
    SPECIALIST = 2    # Специалист
    ADMIN = 3         # Администратор

    id = PrimaryKeyField(primary_key=True)
    name = CharField(unique=True)

    class Meta:
        table_name = "role"