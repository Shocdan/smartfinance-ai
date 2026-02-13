import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


class FinancialPredictor:
    def train_and_predict(self, df, days_ahead=30):

        # Ordenar por fecha
        df = df.sort_values("date")

        # Crear columna acumulativa
        df["cumulative"] = df["amount"].cumsum()

        # Convertir fechas a números
        df["day_number"] = (df["date"] - df["date"].min()).dt.days

        X = df[["day_number"]]
        y = df["cumulative"]

        model = LinearRegression()
        model.fit(X, y)

        # Predecir futuro
        future_days = np.array(
            range(df["day_number"].max(), df["day_number"].max() + days_ahead)
        ).reshape(-1, 1)

        predictions = model.predict(future_days)

        return future_days.flatten(), predictions
