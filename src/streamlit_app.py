import streamlit as st
from agents.csv_agent import CSVAgent
from agents.code_writer_agent import CodeWriterAgent
from agents.sanitize_agent import SanitizeAgent
from agents.exec_agent import ExecAgent

st.title("GitHub Repo Data Query System")

user_query = st.text_input("Ask me anything about the repos…")

if st.button("Run Query"):
    csv_agent = CSVAgent()
    csv_agent.summarize_all_tables()
    table_name, df, summary = csv_agent.select_relevant_table(user_query)

    code_writer = CodeWriterAgent()
    raw_code = code_writer.generate_code(summary, user_query, table_name)

    sanitizer = SanitizeAgent()
    cleaned_code = sanitizer.clean_code(raw_code)

    exec_agent = ExecAgent()
    output, plt_lib = exec_agent.run_code(cleaned_code)

    st.subheader("Query Output:")
    st.text(output)
    if plt_lib:
        st.pyplot(plt_lib)
