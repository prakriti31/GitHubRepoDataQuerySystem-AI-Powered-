# BONUS ASSIGNMENT – SETUP AND EXECUTION GUIDE

---

# PHASE 1 – Environment Setup

## Install Requirements

Go into:

```
Bonus_Assignment_1_YourLastName/src
```

Install dependencies:

```
uv pip install -r requirements.txt
```

## Verify Installation

```
python setup_env_check.py
```

If all packages load successfully, proceed to Phase 2.

---

# PHASE 2 – GitHub Data Extraction

## Step 1 – Set GitHub Token

You need a GitHub Personal Access Token stored as an environment variable.

Linux / Mac:

```
export GITHUB_TOKEN="your_token_here"
```

Windows PowerShell:

```
setx GITHUB_TOKEN "your_token_here"
```

## Step 2 – Run the Data Fetch Script

Inside:

```
Bonus_Assignment_1_YourLastName/src/
```

Run:

```
python fetch_github_data.py
```

## Step 3 – Output Files

When successful, CSV files will appear in:

```
src/data/
```

Examples:

* `issues_meta-llama_llama3.csv`
* `commits_langchain-ai_langgraph.csv`
* `repo_info_openai_openai-cookbook.csv`

These will be used in Phase 3 to load data into PostgreSQL.
