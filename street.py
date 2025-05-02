import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
# MySQL connection function
def get_connection():
    return mysql.connector.connect(
        host="82.180.143.66",
        user="u263681140_students",
        password="testStudents@123",
        database="u263681140_students"
    )

# Function to fetch data
def fetch_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM StreetLight")
    data = cursor.fetchall()
    conn.close()
    return pd.DataFrame(data)

# Login credentials (for demo - consider using secure auth in production)
USER_CREDENTIALS = {
    "admin": "admin123",
    "user": "user123"
}

# Session state to handle login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔒 Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn:
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

# Main app


def main():
    st.title("💡 Street Light Monitoring System")

    df = fetch_data()

    st.subheader("📊 Raw Data")
    st.dataframe(df)

    # Choose what to visualize
    option = st.selectbox("Select parameter to visualize", ["Current", "Voltage"])

    if option == "Current":
        labels = ['Current1', 'Current2', 'Current3']
        values = df[labels].replace('[^0-9.]', '', regex=True).astype(float).sum()
        fig = px.pie(values=values, names=labels, title="Current Distribution")
    else:
        labels = ['Vtg1', 'Vtg2', 'Vtg3']
        values = df[labels].replace('[^0-9.]', '', regex=True).astype(float).sum()
        fig = px.pie(values=values, names=labels, title="Voltage Distribution")

    st.plotly_chart(fig)

if not st.session_state.logged_in:
    login()
else:
    main()
