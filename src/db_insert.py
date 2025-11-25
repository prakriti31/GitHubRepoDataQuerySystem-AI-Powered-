import os
import pandas as pd
from db_connect import get_connection

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")

# ------------------------------
# Helper: Clean CSV
# ------------------------------
def clean_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        
        # Check if dataframe is empty
        if df.empty:
            print(f"⚠️ Skipping empty file: {file_path}")
            return pd.DataFrame()

        # Replace literal string "NaT" with None - multiple approaches for safety
        df.replace("NaT", "", inplace=True)
        df.replace("NaT", None, inplace=True)
        df.replace(pd.NA, None, inplace=True)
        df.replace(pd.NaT, None, inplace=True)
        
        # Also handle any cells that are exactly the string "NaT"
        for col in df.columns:
            df[col] = df[col].apply(lambda x: None if str(x).strip() == "NaT" else x)

        return df
    except pd.errors.EmptyDataError:
        print(f"⚠️ Skipping empty file: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return pd.DataFrame()

# ------------------------------
# Table creation SQL
# ------------------------------
TABLES_SQL = {
    "issues": """
        CREATE TABLE IF NOT EXISTS issues (
            id BIGINT PRIMARY KEY,
            repository_url TEXT,
            number INT,
            title TEXT,
            user_login TEXT,
            state TEXT,
            locked BOOLEAN,
            assignee TEXT,
            assignees TEXT,
            milestone TEXT,
            comments INT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            closed_at TIMESTAMP,
            body TEXT
        );
    """,
    "commits": """
        CREATE TABLE IF NOT EXISTS commits (
            sha TEXT PRIMARY KEY,
            node_id TEXT,
            url TEXT,
            html_url TEXT,
            comments_url TEXT,
            author TEXT,
            committer TEXT,
            parents TEXT
        );
    """,
    "repo_info": """
        CREATE TABLE IF NOT EXISTS repo_info (
            id BIGINT PRIMARY KEY,
            name TEXT,
            full_name TEXT,
            description TEXT,
            html_url TEXT,
            stargazers_count INT,
            watchers_count INT,
            forks_count INT,
            open_issues_count INT,
            language TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            pushed_at TIMESTAMP
        );
    """
}

# ------------------------------
# Create tables
# ------------------------------
def create_tables(conn):
    with conn.cursor() as cur:
        for table, sql_stmt in TABLES_SQL.items():
            cur.execute(sql_stmt)
            print(f"✅ Table '{table}' ensured in DB")
    conn.commit()

# ------------------------------
# Insert issues
# ------------------------------
def insert_issues(conn, df):
    if df.empty:
        print("⚠️ No issues data to insert")
        return

    df_insert = df[[
        "id", "repository_url", "number", "title", "user", "state", "locked",
        "assignee", "assignees", "milestone", "comments", "created_at",
        "updated_at", "closed_at", "body"
    ]].copy()

    # Flatten 'user' JSON to get login
    df_insert["user_login"] = df_insert["user"].apply(lambda x: x.get("login") if isinstance(x, dict) else None)
    df_insert.drop(columns=["user"], inplace=True)

    # Convert numeric columns
    for col in ["comments", "number"]:
        df_insert[col] = pd.to_numeric(df_insert[col], errors="coerce").astype("Int64")

    # Convert datetime columns
    for col in ["created_at", "updated_at", "closed_at"]:
        # First, replace any "NaT" strings
        df_insert[col] = df_insert[col].replace("NaT", None)
        df_insert[col] = df_insert[col].replace(pd.NaT, None)
        # Apply function to handle various cases
        def clean_datetime(x):
            if x is None or x == "" or x == "NaT":
                return None
            if pd.isna(x):
                return None
            if isinstance(x, str):
                if x.strip() in ("NaT", "nan", "NaN", ""):
                    return None
                try:
                    return pd.to_datetime(x).to_pydatetime()
                except:
                    return None
            try:
                return pd.to_datetime(x).to_pydatetime()
            except:
                return None
        df_insert[col] = df_insert[col].apply(clean_datetime)

    # Convert JSON-like columns to string
    for col in ["assignees", "milestone"]:
        df_insert[col] = df_insert[col].apply(lambda x: str(x) if x is not None else None)

    # Replace any remaining NaN with None
    df_insert = df_insert.where(pd.notnull(df_insert), None)

    with conn.cursor() as cur:
        for idx, row in df_insert.iterrows():
            # Final safety check: convert any remaining "NaT" strings to None
            row_values = []
            for val in [row["id"], row["repository_url"], row["number"], row["title"],
                       row["user_login"], row["state"], row["locked"], row["assignee"],
                       row["assignees"], row["milestone"], row["comments"], row["created_at"],
                       row["updated_at"], row["closed_at"], row["body"]]:
                # Check for NaT in multiple ways
                if val is pd.NaT:
                    row_values.append(None)
                elif pd.isna(val):
                    row_values.append(None)
                elif isinstance(val, str) and val.strip() in ("NaT", "nan", "NaN"):
                    row_values.append(None)
                else:
                    row_values.append(val)
            
            # Debug print for problematic row
            if any(str(v) == "NaT" for v in row_values):
                print(f"⚠️ Found NaT in row {idx}: {row_values}")
            
            cur.execute("""
                INSERT INTO issues (
                    id, repository_url, number, title, user_login, state, locked,
                    assignee, assignees, milestone, comments, created_at, updated_at,
                    closed_at, body
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO NOTHING;
            """, tuple(row_values))
    conn.commit()
    print(f"💾 Inserted {len(df_insert)} issues rows")

# ------------------------------
# Insert commits
# ------------------------------
def insert_commits(conn, df):
    if df.empty:
        print("⚠️ No commits data to insert")
        return

    df_insert = df[[
        "sha","node_id","url","html_url","comments_url","author","committer","parents"
    ]].copy()

    # Flatten author/committer if nested
    for col in ["author","committer"]:
        df_insert[col] = df_insert[col].apply(lambda x: str(x) if x is not None else None)

    # Convert parents (list) to string
    df_insert["parents"] = df_insert["parents"].apply(lambda x: str(x) if x else None)

    # Replace NaN with None
    df_insert = df_insert.where(pd.notnull(df_insert), None)

    with conn.cursor() as cur:
        for _, row in df_insert.iterrows():
            cur.execute("""
                INSERT INTO commits (
                    sha,node_id,url,html_url,comments_url,author,committer,parents
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (sha) DO NOTHING;
            """, tuple(row))
    conn.commit()
    print(f"💾 Inserted {len(df_insert)} commits rows")

# ------------------------------
# Insert repo_info
# ------------------------------
def insert_repo_info(conn, df):
    if df.empty:
        print("⚠️ No repo info data to insert")
        return

    df_insert = df[[
        "id","name","full_name","description","html_url","stargazers_count",
        "watchers_count","forks_count","open_issues_count","language",
        "created_at","updated_at","pushed_at"
    ]].copy()

    # Convert numeric columns
    for col in ["stargazers_count","watchers_count","forks_count","open_issues_count"]:
        df_insert[col] = pd.to_numeric(df_insert[col], errors="coerce").astype("Int64")

    # Convert datetime columns
    for col in ["created_at","updated_at","pushed_at"]:
        # First, replace any "NaT" strings
        df_insert[col] = df_insert[col].replace("NaT", None)
        df_insert[col] = df_insert[col].replace(pd.NaT, None)
        # Apply function to handle various cases
        def clean_datetime(x):
            if x is None or x == "" or x == "NaT":
                return None
            if pd.isna(x):
                return None
            if isinstance(x, str):
                if x.strip() in ("NaT", "nan", "NaN", ""):
                    return None
                try:
                    return pd.to_datetime(x).to_pydatetime()
                except:
                    return None
            try:
                return pd.to_datetime(x).to_pydatetime()
            except:
                return None
        df_insert[col] = df_insert[col].apply(clean_datetime)

    # Replace any remaining NaN with None
    df_insert = df_insert.where(pd.notnull(df_insert), None)

    with conn.cursor() as cur:
        for idx, row in df_insert.iterrows():
            # Final safety check: convert any remaining "NaT" strings to None
            row_values = []
            for val in row:
                # Check for NaT in multiple ways
                if val is pd.NaT:
                    row_values.append(None)
                elif pd.isna(val):
                    row_values.append(None)
                elif isinstance(val, str) and val.strip() in ("NaT", "nan", "NaN"):
                    row_values.append(None)
                else:
                    row_values.append(val)
            row_values = tuple(row_values)
            
            cur.execute("""
                INSERT INTO repo_info (
                    id,name,full_name,description,html_url,stargazers_count,
                    watchers_count,forks_count,open_issues_count,language,
                    created_at,updated_at,pushed_at
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO NOTHING;
            """, row_values)
    conn.commit()
    print(f"💾 Inserted {len(df_insert)} repo_info rows")

# ------------------------------
# Main
# ------------------------------
def main():
    conn = get_connection()
    create_tables(conn)

    # Insert issues
    for file in os.listdir(DATA_FOLDER):
        if file.startswith("issues_") and file.endswith(".csv"):
            df = clean_csv(os.path.join(DATA_FOLDER, file))
            insert_issues(conn, df)

    # Insert commits
    for file in os.listdir(DATA_FOLDER):
        if file.startswith("commits_") and file.endswith(".csv"):
            df = clean_csv(os.path.join(DATA_FOLDER, file))
            insert_commits(conn, df)

    # Insert repo info
    for file in os.listdir(DATA_FOLDER):
        if file.startswith("repo_info_") and file.endswith(".csv"):
            df = clean_csv(os.path.join(DATA_FOLDER, file))
            insert_repo_info(conn, df)

    conn.close()
    print("🎉 PHASE 3 COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()