import streamlit as st
import mysql.connector
import pandas as pd
import plotly.graph_objects as go

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

# Tab 1: Main dashboard function
def dashboard():
    st.title("💡 Street Light Monitoring System")

    df = fetch_data()

    st.subheader("📊 Raw Data")
    st.dataframe(df)

    option = st.selectbox("Select parameter to visualize", ["Current", "Voltage"])

    if option == "Current":
        labels = ['Current1', 'Current2', 'Current3']
    else:
        labels = ['Vtg1', 'Vtg2', 'Vtg3']

    # Ensure 'id' column is numeric
    df['id'] = pd.to_numeric(df['id'], errors='coerce')

    # Get the row with maximum 'id'
    latest = df.loc[df['id'].idxmax()]

    # Raw display values with units
    display_labels = [f"{col}: {latest[col]}" for col in labels]

    # Numeric values for plotting
    numeric_values = pd.to_numeric(latest[labels].replace('[^0-9.]', '', regex=True), errors='coerce')

    fig = go.Figure(data=[go.Pie(
        labels=display_labels,
        values=numeric_values,
        textinfo='label',
        hoverinfo='label+value'
    )])

    fig.update_layout(title="Distribution of " + option)

    st.plotly_chart(fig)

# Tab 2: Bulb status display
def bulb_status():
    st.title("💡 Bulb Status")
    st.header("📌 Current Bulb Status Information")
    
    df = fetch_data()
    latest = df.loc[df['id'].idxmax()]
    
    # You can customize this as needed depending on available columns
    bulb_info = {
        "Bulb1": latest.get("Bulb1", "Unknown"),
        "Bulb2": latest.get("Bulb2", "Unknown"),
        "Bulb3": latest.get("Bulb3", "Unknown")
    }

    for key, status in bulb_info.items():
        st.write(f"🔹 {key} Status: {status}")

# Main app with tabs
def main_app():
    tab1, tab2 = st.tabs(["📊 Dashboard", "💡 Bulb Status"])
    
    with tab1:
        dashboard()
    
    with tab2:
        bulb_status()

# Entry point
if not st.session_state.logged_in:
    login()
else:
    main_app()
