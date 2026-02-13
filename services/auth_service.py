from core.security import hash_password, verify_password
from infrastructure.repositories import UserRepository


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
        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user
