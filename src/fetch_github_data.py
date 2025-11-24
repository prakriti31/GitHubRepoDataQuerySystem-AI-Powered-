import os
import requests
import pandas as pd
from datetime import datetime
from utils import get_github_token, get_date_range
from repos_list import REPOS

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_FOLDER, exist_ok=True)

BASE_URL = "https://api.github.com"

def fetch_issues(repo, token, since):
    print(f"📥 Fetching issues for {repo}...")
    url = f"{BASE_URL}/repos/{repo}/issues"
    params = {"since": since, "state": "all", "per_page": 100}
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(url, params=params, headers=headers)
    r.raise_for_status()
    return r.json()

def fetch_commits(repo, token, since):
    print(f"📥 Fetching commits for {repo}...")
    url = f"{BASE_URL}/repos/{repo}/commits"
    params = {"since": since, "per_page": 100}
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(url, params=params, headers=headers)
    r.raise_for_status()
    return r.json()

def fetch_repo_metadata(repo, token):
    print(f"📥 Fetching metadata for {repo}...")
    url = f"{BASE_URL}/repos/{repo}"
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    out_path = os.path.join(DATA_FOLDER, filename)
    df.to_csv(out_path, index=False)
    print(f"💾 Saved: {out_path}")

if __name__ == "__main__":
    token = get_github_token()
    since = get_date_range()

    for repo in REPOS:
        repo_clean = repo.replace("/", "_")

        # Fetch issues
        issues = fetch_issues(repo, token, since)
        save_to_csv(issues, f"issues_{repo_clean}.csv")

        # Fetch commits
        commits = fetch_commits(repo, token, since)
        save_to_csv(commits, f"commits_{repo_clean}.csv")

        # Fetch metadata (stars, forks, watchers)
        meta = fetch_repo_metadata(repo, token)
        save_to_csv([meta], f"repo_info_{repo_clean}.csv")

    print("\n🎉 PHASE 2 COMPLETED SUCCESSFULLY!")
