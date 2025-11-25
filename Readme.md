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

---

# Phase 3 - Store GitHub Data in PostgreSQL

## 1. Install PostgreSQL

1. Go to [https://www.postgresql.org/download/](https://www.postgresql.org/download/) and download PostgreSQL for your operating system.
2. Install PostgreSQL using default settings. Make note of your **username** (default: postgres) and **password**.

## 2. Start PostgreSQL

* **Mac/Linux**:

  * Open terminal
  * Start PostgreSQL service:
    pg_ctl -D /usr/local/var/postgres start
  * Or, if installed via Homebrew:
    brew services start postgresql

* **Windows**:

  * Open “pgAdmin” or “SQL Shell (psql)”
  * Start the PostgreSQL server from the application

## 3. Create the Database

1. Open terminal or psql shell.
2. Run the following command to create a new database called `github_data`:
   createdb github_data
3. Verify the database exists:
   psql -l

## 4. Set Environment Variables (Optional)

* The Python scripts use default PostgreSQL settings:
  host = localhost
  port = 5432
  dbname = github_data
  user = postgres
  password = postgres

* You can override by setting environment variables:
  export PG_HOST=localhost
  export PG_PORT=5432
  export PG_DB=github_data
  export PG_USER=postgres
  export PG_PASSWORD=postgres

## 5. Install Python Dependencies

1. Open terminal and navigate to `src/` folder.
2. Run:
   pip install -r requirements.txt

## 6. Place Phase 2 CSV Files

* Make sure your CSV files from Phase 2 are inside `src/data/`:

  * issues_<repo>.csv
  * commits_<repo>.csv
  * repo_info_<repo>.csv

## 7. Run Phase 3 - Insert Data into PostgreSQL

1. In terminal, navigate to `src/` folder.
2. Run:
   python db_insert.py

* The script will:

  * Create tables `issues`, `commits`, `repo_info` if they don’t exist
  * Clean NaN values in CSVs
  * Insert data into PostgreSQL
  * Skip empty CSV files

## 8. Verify Data in Database

1. Open PostgreSQL shell:
   psql -U postgres -d github_data

2. Run queries to check table contents:
   SELECT COUNT(*) FROM issues;
   SELECT COUNT(*) FROM commits;
   SELECT COUNT(*) FROM repo_info;

3. You can also preview some rows:
   SELECT * FROM issues LIMIT 5;
   SELECT * FROM commits LIMIT 5;
   SELECT * FROM repo_info LIMIT 5;

* If counts match the number of rows in your CSVs, Phase 3 ran successfully.

## ✅ Notes

* Empty CSVs are automatically skipped.
* Nested JSON fields in issues (like user) are flattened.
* NaN values in CSVs are converted to SQL NULL.
* All inserts use `ON CONFLICT DO NOTHING` to avoid duplicates.

---
