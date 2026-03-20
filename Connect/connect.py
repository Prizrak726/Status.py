import os
from peewee import SqliteDatabase
from dotenv import load_dotenv

load_dotenv()

def connect():
    db_url = os.getenv('DATABASE_URL', 'sqlite:///instance/db.sqlite3')
    if db_url.startswith('sqlite://'):
        db_path = db_url.replace('sqlite://', '')
        # Создаём директорию, если её нет
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return SqliteDatabase(db_path)
    else:
        raise Exception(f"Неподдерживаемый тип БД: {db_url}. Ожидается sqlite://...")

if __name__ == '__main__':
    db = connect()
    if db:
        print("Подключение к SQLite успешно")
        print(db.connect())
    else:
        print("Не удалось подключиться к БД")