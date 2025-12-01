import os
from openai import OpenAI

class CodeWriterAgent:
    """
    Generates Python code for GitHub Repo Data Query System.
    Fixed to handle missing datetime in commits table safely.
    DOES NOT break Prophet queries on issues table.
    """

    def __init__(self, temperature=0):
        self.temperature = temperature
        api_key = os.environ.get("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY not set.")

        self.client = OpenAI(api_key=api_key)

    def generate_code(self, table_summary, user_query, table_name):

        prompt = f"""
You are an expert data engineer working with a GitHub analytics PostgreSQL database named 'github_data'.

The current table is: {table_name}

Table summary:
{table_summary}

You MUST generate a COMPLETE, EXECUTABLE Streamlit Python script.

=======================================================
 REQUIRED DATABASE CONNECTION BLOCK
=======================================================

import psycopg2
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="github_data",
    user="postgres",
    password="postgres"
)

cursor = conn.cursor()
cursor.execute("SET search_path TO public;")

=======================================================
 AFTER DATAFRAME LOAD (MANDATORY)
=======================================================

1. Load data into pandas as df.
2. Print columns using: 
   st.write("Columns:", df.columns.tolist())

=======================================================
 DATETIME COLUMN HANDLING (CRITICAL - DO NOT BREAK)
=======================================================

IF table_name == "issues":

✅ Use ONLY:
   created_at → for created issues Prophet
   closed_at  → for closed issues Prophet

✅ Convert only those columns using:
   df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
   df["closed_at"]  = pd.to_datetime(df["closed_at"], errors="coerce")

✅ DO NOT try to auto-detect any datetime column

-------------------------------------------------------

IF table_name == "commits":

🚫 DO NOT use:
   - created_at
   - closed_at
   - commit_date
   - any guessed datetime

✅ Check if ANY column contains the words:
   "date", "time", "timestamp"

✅ If one EXISTS:
   Use it safely with pd.to_datetime(..., errors="coerce")

✅ If NONE exists:
   DO NOT CRASH
   Instead:
     - Display warning in Streamlit:
       st.warning("Commits table has NO datetime column - forecasting not possible")
     - Return a BAR CHART showing total commits (pulls) per repo
     - This FULLY satisfies the assignment requirement

=======================================================
 USER QUERY
=======================================================

"{user_query}"

=======================================================
 OUTPUT MODE RULES (BASED ON PDF)
=======================================================

MODE 1 — TEXT ONLY:
- "Which repo..."
- "Which day..."

→ Use st.write() only

MODE 2 — TABLE ONLY:
- "Create a table..."

→ Use st.dataframe() only

MODE 3 — CHARTS:
- Line chart
- Bar chart
- Pie chart
- Stacked chart

→ Use Plotly or matplotlib
→ Show with st.plotly_chart() or st.pyplot()

MODE 4 — FORECAST (IMPORTANT):

✅ Prophet:
   - Only for issues
   - Uses created_at or closed_at
   - Forecast 30 days
   - One chart per repo

✅ StatsModels (SARIMAX):
   - Commits or Pulls
   - ONLY if datetime column exists
   - Otherwise fallback to Bar Chart

=======================================================
 FORECASTING RULES
=======================================================

Per repository:

1. Filter by repository_url OR url
2. Set datetime index
3. Resample DAILY
4. Fill missing days = 0
5. Fit model
6. Forecast 30 days
7. Rename column:
   - forecasted_issues
   - forecasted_commits
   - forecasted_pulls

8. Plot:
   - Historical
   - Forecast
   - Title: "30-Day Forecast for <repo>"

=======================================================
 ABSOLUTE RULES
=======================================================

✅ NO hard-coded datetime columns in commits
✅ NO crashing if datetime not found
✅ Issues table must STILL use Prophet correctly
✅ Must import:
   pandas, streamlit, psycopg2, matplotlib/plotly, prophet, statsmodels
✅ Do NOT write into database
✅ ONLY output executable Python CODE, no explaination, no text. ONLY CODE.

BEGIN CODE:
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature
        )

        return response.choices[0].message.content
