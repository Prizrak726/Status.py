from peewee import *

def connect():
    try: # удачная попытка
        db = MySQLDatabase(
            "yanao",
            user="root",
            passwd="",
            host="127.0.0.1",
            port=3306,
        )
        return db
    except : # неудачная попытка
        print(f'Ошибка')
        return None

if __name__ == '__main__':
    print(connect().connect())