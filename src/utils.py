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
