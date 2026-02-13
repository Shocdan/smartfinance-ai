from core.security import hash_password, verify_password
from infrastructure.repositories import UserRepository
from datetime import datetime, timedelta, timezone


MAX_ATTEMPTS = 5
LOCK_TIME = timedelta(minutes=15)


class AuthService:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register_user(self, email: str, password: str):
        existing = self.user_repository.get_by_email(email)
        if existing:
            raise Exception("User already exists")

        hashed = hash_password(password)
        return self.user_repository.create(email, hashed)

    def authenticate(self, email: str, password: str):
        user = self.user_repository.get_by_email(email)
        now = datetime.now(timezone.utc)

        if not user:
            return None

        # 🔒 Verificar si está bloqueado
        if user.locked_until and user.locked_until > now:
            return None

        if not verify_password(password, user.password_hash):
            user.failed_attempts += 1
            user.last_failed_attempt = now

            if user.failed_attempts >= MAX_ATTEMPTS:
                user.locked_until = now + LOCK_TIME

            self.user_repository.update(user)
            return None

        # ✅ Login correcto
        user.failed_attempts = 0
        user.locked_until = None
        self.user_repository.update(user)

        return user
