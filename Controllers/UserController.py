from typing import Optional, Iterable

from bcrypt import hashpw, gensalt, checkpw
from peewee import IntegrityError, DoesNotExist

from Models.Users import Users
from Models.Role import Role


class UserController:
    """
    Контроллер для работы с пользователями (регистрация, авторизация, CRUD).
    """

    @classmethod
    def list_users(cls) -> Iterable[Users]:
        """
        Получить всех пользователей.
        """
        return Users.select()

    @classmethod
    def get_user(cls, user_id: int) -> Optional[Users]:
        """
        Получить пользователя по id.
        """
        try:
            return Users.get_by_id(user_id)
        except DoesNotExist:
            return None

    @classmethod
    def _resolve_role(cls, role_id: Optional[int] = None, role_name: Optional[str] = None) -> Role:
        """
        Внутренний метод: определить роль по id или имени.
        Если параметры не заданы, используется роль обычного пользователя.
        """
        if role_id is not None:
            return Role.get_by_id(role_id)
        if role_name:
            return Role.get(Role.name == role_name)
        # по умолчанию обычный пользователь
        return Role.get_by_id(Role.USER)

    @classmethod
    def register(
        cls,
        name: str,
        login: str,
        password: str,
        role_id: Optional[int] = None,
        role_name: Optional[str] = None,
    ) -> tuple[bool, str | Users]:
        """
        Регистрация нового пользователя.

        :return: (успех, сообщение или созданный пользователь)
        """
        # Сначала явно проверяем, что логин свободен,
        # чтобы не путать эту ошибку с другими IntegrityError.
        existing = Users.get_or_none(Users.login == login)
        if existing is not None:
            return False, "Пользователь с таким логином уже существует"

        try:
            role = cls._resolve_role(role_id=role_id, role_name=role_name)

            # Если имя не указано, используем логин как отображаемое имя
            if not name:
                name = login

            raw = password.encode("utf-8")
            hashed = hashpw(raw, gensalt()).decode("utf-8")

            user = Users.create(
                name=name,
                login=login,
                password=hashed,
                role=role,
            )
            return True, user
        except IntegrityError as exc:
            # Если в старой схеме БД поле name или другой столбец помечен как unique,
            # попробуем автоматически подобрать уникальное отображаемое имя и
            # повторить сохранение, чтобы не блокировать регистрацию.
            msg = str(exc)
            if "Duplicate entry" in msg and "name" in msg:
                try:
                    fallback_name = f"{name}_{Users.select().count() + 1}"
                    user = Users.create(
                        name=fallback_name,
                        login=login,
                        password=hashed,
                        role=role,
                    )
                    return True, user
                except Exception as exc2:  # noqa: BLE001
                    return False, f"Ошибка сохранения пользователя: {exc2}"

            # Любая другая ошибка целостности (не только уникальность логина/имени)
            return False, f"Ошибка сохранения пользователя: {exc}"
        except Exception as exc:  # noqa: BLE001
            return False, f"Ошибка регистрации пользователя: {exc}"

    @classmethod
    def authenticate(cls, login: str, password: str) -> Optional[Users]:
        """
        Авторизация пользователя по логину и паролю.
        Возвращает объект Users при успехе, иначе None.
        """
        try:
            user = Users.get(Users.login == login)
        except DoesNotExist:
            return None

        try:
            raw = password.encode("utf-8")
            stored = user.password.encode("utf-8")
            if checkpw(raw, stored):
                return user
            return None
        except Exception:  # noqa: BLE001
            return None

    @classmethod
    def update_user(cls, user_id: int, **fields) -> tuple[bool, str]:
        """
        Обновить данные пользователя.
        Поддерживаются поля: name, login, password, role (id или имя).
        """
        try:
            user = Users.get_by_id(user_id)
        except DoesNotExist:
            return False, "Пользователь не найден"

        # Обработка роли
        role_id = fields.pop("role_id", None)
        role_name = fields.pop("role_name", None)
        if role_id is not None or role_name is not None:
            try:
                user.role = cls._resolve_role(role_id=role_id, role_name=role_name)
            except DoesNotExist:
                return False, "Указанная роль не найдена"

        # Обработка пароля
        if "password" in fields and fields["password"]:
            raw = fields["password"].encode("utf-8")
            user.password = hashpw(raw, gensalt()).decode("utf-8")
            fields.pop("password")

        # Простой маппинг остальных полей
        for field_name, value in fields.items():
            if hasattr(user, field_name):
                setattr(user, field_name, value)

        try:
            user.save()
            return True, "Пользователь обновлён"
        except IntegrityError:
            return False, "Логин уже занят другим пользователем"
        except Exception as exc:  # noqa: BLE001
            return False, f"Ошибка обновления пользователя: {exc}"

    @classmethod
    def delete_user(cls, user_id: int) -> tuple[bool, str]:
        """
        Удалить пользователя по id.
        """
        try:
            user = Users.get_by_id(user_id)
        except DoesNotExist:
            return False, "Пользователь не найден"

        try:
            user.delete_instance()
            return True, "Пользователь удалён"
        except Exception as exc:  # noqa: BLE001
            return False, f"Ошибка удаления пользователя: {exc}"


__all__ = ["UserController"]

