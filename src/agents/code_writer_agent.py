import os
import openai

class CodeWriterAgent:
    """
    Generates Python code for a query using GPT-4o-mini.
    """

    def __init__(self, temperature=0):
        self.temperature = temperature
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set.")
        openai.api_key = api_key

    def generate_code(self, table_summary, user_query, table_name):
        prompt = f"""
You have the table '{table_name}' inside PostgreSQL database 'github_data'.
Table summary:
{table_summary}

Write a COMPLETE, EXECUTABLE Python program that:

1. Connects to Postgres using:

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

2. Loads the relevant table(s) into pandas DataFrame(s).
3. Answers the user query: "{user_query}"
4. Prints textual/table output OR generates charts (matplotlib/plotly).
5. Contains no placeholders and no pseudo-code.
6. Uses matplotlib/plotly/seaborn for charts.
7. Uses Prophet for forecasting (imported as: from prophet import Prophet)
8. Uses statsmodels for ARIMA/SARIMA forecasting.
9. Display the results as a clean, styled table inside Streamlit using st.dataframe or st.table (NOT print).
10. Give only detail which is asked, plot graphs only when asked.
11. Always rename forecast column to something unique like forecasted_commits to avoid conflicts.
12. Do not attempt database insertions for the forecast output; just display it.

Rules for generating code:

1. If the query is textual-only:
   - Output ONLY text.
   - NO charts, plots, or figures.
   - Print results clearly using pandas DataFrame or plain text.

2. If the query is tabular:
   - Output a clean table (pandas DataFrame) only.
   - Do not generate charts unless explicitly asked.

3. If the query is a chart/graph:
   - Output a figure using matplotlib or plotly.
   - No raw DataFrame output; chart should reflect the query.

4. If the query is a forecast:
   - Use Prophet for issues created or closed.
   - Use statsmodels (ARIMA/SARIMA) for commits or pull requests.
   - Forecast for the next 30 days.
   - Plot the forecast with proper x/y labels and title.

When the user query involves forecasting with Statsmodels:

1. Identify the correct table:
   - Pull requests → 'commits' table
   - Commits → 'commits' table
   - Issues created/closed → 'issues' table

2. For each repository:
   - Filter data for that repository.
   - Convert date column to datetime.
   - Set DatetimeIndex.
   - Resample daily using df.resample('D').sum().fillna(0).
   
3. Fit a SARIMAX model for 30-day forecast.
4. Create forecast DataFrame with columns: ['date', 'forecasted_<metric>'] 
   where <metric> is commits, pull_requests, or issues.
5. Display results in Streamlit using st.dataframe().
6. If the user query is textual or tabular, do NOT generate plots.
7. If the user query explicitly asks for a chart, plot it using matplotlib or plotly.
8. Do NOT insert/update any tables in the database.
9. Only output executable Python code.

Return ONLY valid executable Python code.
"""

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature
        )

        return response.choices[0].message.content
