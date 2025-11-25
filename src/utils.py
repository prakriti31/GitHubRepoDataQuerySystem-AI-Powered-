import os
from datetime import datetime, timedelta

def get_github_token():
    token = os.getenv("GITHUB_TOKEN")
    if token is None:
        raise ValueError("❌ ERROR: GITHUB_TOKEN not found in environment variables.")
    return token

def get_date_range():
    today = datetime.utcnow()
    since = today - timedelta(days=60)
    return since.isoformat() + "Z"
import pandas as pd
import os

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")

def clean_csv(file_path):
    """
    Reads CSV, replaces NaN with None (for SQL insertion), returns DataFrame
    """
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        return pd.DataFrame()  # empty DF

    df = pd.read_csv(file_path)
    df = df.where(pd.notnull(df), None)
    return df

def flatten_user_column(df, col="user"):
    if col in df.columns:
        df[col+"_login"] = df[col].apply(lambda x: x["login"] if isinstance(x, dict) else None)
        df.drop(columns=[col], inplace=True)
    return df