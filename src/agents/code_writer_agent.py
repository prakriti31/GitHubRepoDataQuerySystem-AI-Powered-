# agents/code_writer_agent.py

import os
import openai

class CodeWriterAgent:
    """
    Generates Python code for a query using GPT-4o-mini.
    Fully compatible with OpenAI Python SDK v1+ and Python 3.12
    """
    def __init__(self, temperature=0):
        self.temperature = temperature
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in environment variables")
        openai.api_key = self.api_key

    def generate_code(self, table_summary, user_query, table_name):
        prompt = f"""
You have access to a table '{table_name}' with summary:
{table_summary}

Write a complete Python program using pandas/matplotlib/plotly/prophet/statsmodels
to answer the following user query: "{user_query}".
Requirements:
1. Works with data from Postgres.
2. Produces textual/tabular output OR charts as needed.
3. Output ONLY executable Python code.
"""
        # New v1+ API
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature
        )

        code = response.choices[0].message.content
        return code
