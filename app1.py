from dotenv import load_dotenv
import mysql.connector
import os
import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import pymysql
import re  # Import regex for validation

# Load environment variables
load_dotenv()

# Configure the Gemini API with the key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text

def extract_sql(response):
    sql_pattern = r"(SELECT|INSERT|UPDATE|DELETE)\s.+;"
    match = re.search(sql_pattern, response, re.IGNORECASE | re.DOTALL)
    return match.group(0) if match else None

def read_sql_query(sql):
    conn = pymysql.connect(host="localhost", user="12345", password="12345", database="telecom_chatbot")
    if conn.open:
        print("Connection successful")
    
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows

# Prompt for Gemini
prompt = ["""
You are an expert in converting English questions to SQL queries and a skilled sentiment analyst.
The MySQL database telecom_chatbot includes 4 tables:
1. customer: id, name, country, state, status
2. issue_history: issue_type, dept_id, description, id, PRIORITY
3. agent_table: agent_id, agent_name, agent_department, agent_availability, dept_id
4. subscription: id, GB

Special Instructions:
- Start by acknowledging the user's issue with an apologizing message.
- If the user types "I am facing," classify and process the issue.
- Generate a ticket ID by concatenating customer_id, department_id, and priority using "-".
- Summarize and classify the issue based on issue_type in the issue_history table.
- Retrieve department_id and check agent availability (agent_availability = 1) in agent_table.
- For general queries like "hi" or "hello," respond conversationally without SQL queries.
"""]

# Streamlit page setup
st.set_page_config(page_title="Telecom Query Assistant", layout="wide")

st.markdown("""
<style>
body {
    background-color: #f0f4f8;
    font-family: 'Arial', sans-serif;
}
header {
    background-color: #0056d2;
    color: white;
    padding: 10px;
    border-radius: 5px;
    text-align: center;
}
h1 {
    color: #0056d2;
}
.query-box {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
}
.response-box {
    background-color: #e3f2fd;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
}
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("<header><h1>Telecom Query Assistant</h1></header>", unsafe_allow_html=True)

# UI Layout
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="query-box">', unsafe_allow_html=True)
    st.subheader("Submit Your Query")
    question = st.text_input("Input your question:", key="input")
    submit = st.button("Ask the question")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="response-box">', unsafe_allow_html=True)
    st.subheader("Response")
    if submit:
        if not question.strip():
            st.error("Please enter a valid question or issue.")
        else:
            if question.lower() in ["hi", "hello"]:
                st.write("Hello! How can I assist you today?")
            else:
                response = get_gemini_response(question, prompt)
                sql_query = extract_sql(response)
                if sql_query:
                    try:
                        results = read_sql_query(sql_query)
                        if results:
                            for row in results:
                                st.write(row)
                        else:
                            st.write("No results found.")
                    except pymysql.err.ProgrammingError as e:
                        st.error(f"SQL Error: {e}")
                else:
                    st.write(response)
    st.markdown("</div>", unsafe_allow_html=True)

# HTML Game (Flappy Bird)
st.markdown("<h2>Flappy Bird Game</h2>", unsafe_allow_html=True)
flappy_bird_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
    body { text-align: center; }
    </style>
</head>
<body>
    <iframe src="https://cdn.rawgit.com/nebez/floppybird/master/index.html" width="500" height="700"></iframe>
</body>
</html>
"""
components.html(flappy_bird_html, height=700)
