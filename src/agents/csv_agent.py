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
        cursor = conn.cursor()
        cursor.execute("SET search_path TO public;")
        
        for table in self.tables:
            try:
                df = pd.read_sql(f"SELECT * FROM {table}", conn)
                self.dataframes[table] = df
                if df.empty:
                    self.summaries[table] = f"Table {table} is EMPTY."
                else:
                    cols = list(df.columns)
                    self.summaries[table] = f"Rows={len(df)}, Cols={len(cols)}, Columns={cols}"
            except Exception as e:
                self.summaries[table] = f"Error reading {table}: {e}"
                self.dataframes[table] = pd.DataFrame()

        conn.close()
        return self.summaries, self.dataframes

    def select_relevant_table(self, user_query):
        q = user_query.lower()
        for table, kws in TABLE_KEYWORDS.items():
            if any(kw in q for kw in kws):
                return table, self.dataframes[table], self.summaries[table]
        return "issues", self.dataframes["issues"], self.summaries["issues"]
