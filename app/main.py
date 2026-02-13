import os
import sys

import streamlit as st

# 🔧 Asegura que Python encuentre las carpetas del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.database import Base, SessionLocal, engine
from infrastructure.repositories import UserRepository
from services.auth_service import AuthService

# 🗄 Crear tablas si no existen
Base.metadata.create_all(bind=engine)


def get_auth_service():
    db = SessionLocal()
    user_repo = UserRepository(db)
    return AuthService(user_repo)


def login_view(auth_service):
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = auth_service.authenticate(email, password)
        if user:
            st.session_state["user_id"] = user.id
            st.session_state["email"] = user.email
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")


def register_view(auth_service):
    st.subheader("Register")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        try:
            auth_service.register_user(email, password)
            st.success("User created successfully")
        except Exception as e:
            st.error(str(e))


def dashboard():
    import matplotlib.pyplot as plt
    import pandas as pd

    from infrastructure.repositories import TransactionRepository
    from ml.predictor import FinancialPredictor

    st.title("SmartFinance AI Dashboard 💰")
    st.write(f"Welcome {st.session_state['email']}")

    db = SessionLocal()
    transaction_repo = TransactionRepository(db)

    # ---------------------------
    # ADD TRANSACTION
    # ---------------------------
    st.subheader("Add Transaction")

    amount = st.number_input("Amount", step=1.0)
    category = st.selectbox("Category", ["Food", "Rent", "Salary", "Other"])
    description = st.text_input("Description")

    if st.button("Add"):
        transaction_repo.create(
            st.session_state["user_id"], amount, category, description
        )
        st.success("Transaction added")
        st.rerun()

    # ---------------------------
    # LOAD DATA
    # ---------------------------
    transactions = transaction_repo.get_by_user(st.session_state["user_id"])

    if not transactions:
        st.info("No transactions yet")
        return

    data = [
        {
            "amount": t.amount,
            "category": t.category,
            "description": t.description,
            "date": t.created_at,
        }
        for t in transactions
    ]

    df = pd.DataFrame(data)

    # ---------------------------
    # METRICS
    # ---------------------------
    total_income = df[df["amount"] > 0]["amount"].sum()
    total_expense = df[df["amount"] < 0]["amount"].sum()
    balance = df["amount"].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Income", f"${total_income:.2f}")
    col2.metric("Total Expenses", f"${total_expense:.2f}")
    col3.metric("Balance", f"${balance:.2f}")

    # ---------------------------
    # CATEGORY CHART
    # ---------------------------
    st.subheader("Spending by Category")

    category_summary = df.groupby("category")["amount"].sum()

    st.bar_chart(category_summary)

    # ---------------------------
    # PREDICTION
    # ---------------------------
    st.subheader("Balance Prediction (Next 30 Days)")

    if len(df) > 3:  # mínimo datos
        predictor = FinancialPredictor()
        future_days, predictions = predictor.train_and_predict(df)

        fig, ax = plt.subplots()
        ax.plot(predictions)
        ax.set_title("Predicted Cumulative Balance")
        ax.set_xlabel("Future Days")
        ax.set_ylabel("Balance")

        st.pyplot(fig)
    else:
        st.info("Not enough data for prediction")

    # ---------------------------
    # TRANSACTION TABLE
    # ---------------------------
    st.subheader("All Transactions")
    st.dataframe(df)

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()


def main():
    st.set_page_config(page_title="SmartFinance AI", layout="centered")

    auth_service = get_auth_service()

    # Si el usuario NO está logueado
    if "user_id" not in st.session_state:
        menu = ["Login", "Register"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Login":
            login_view(auth_service)
        else:
            register_view(auth_service)

    # Si el usuario está logueado
    else:
        dashboard()


if __name__ == "__main__":
    main()
