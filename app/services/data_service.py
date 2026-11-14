import pandas as pd

from app.core.config import settings


def load_transactions():

    df = pd.read_csv(settings.transactions_file)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        utc=True
    )

    return df.to_dict(orient="records")
