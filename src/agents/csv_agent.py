import pandas as pd
from db_connect import get_connection
from .table_mapping import TABLE_KEYWORDS

class CSVAgent:
    def __init__(self, tables=["issues", "commits", "repo_info"]):
        self.tables = tables
        self.summaries = {}
        self.dataframes = {}

    def summarize_all_tables(self):
        conn = get_connection()
        for table in self.tables:
            try:
                df = pd.read_sql(f"SELECT * FROM {table}", conn)
                self.dataframes[table] = df
                if df.empty:
                    self.summaries[table] = f"The table {table} is empty."
                else:
                    self.summaries[table] = f"Table {table} has {len(df)} rows and {len(df.columns)} columns: {list(df.columns)}"
            except Exception as e:
                self.summaries[table] = f"Error accessing table {table}: {e}"
                self.dataframes[table] = pd.DataFrame()
        conn.close()
        return self.summaries, self.dataframes

    def select_relevant_table(self, user_query):
        query_lower = user_query.lower()
        for table, kws in TABLE_KEYWORDS.items():
            if any(kw in query_lower for kw in kws):
                return table, self.dataframes[table], self.summaries[table]
        return "issues", self.dataframes["issues"], self.summaries["issues"]
