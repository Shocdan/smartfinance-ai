from sqlalchemy.orm import Session

from domain.entities import Transaction, User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def create(self, email: str, password_hash: str):
        user = User(email=email, password_hash=password_hash)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


class TransactionRepository:
    def __init__(self, db):
        self.db = db

    def create(self, user_id, amount, category, description):
        transaction = Transaction(
            user_id=user_id, amount=amount, category=category, description=description
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def get_by_user(self, user_id):
        return self.db.query(Transaction).filter(Transaction.user_id == user_id).all()
