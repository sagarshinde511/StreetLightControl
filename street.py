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

# Function to fetch all data
def fetch_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM StreetLightStatus")
    data = cursor.fetchall()
    conn.close()
    return pd.DataFrame(data)

# Function to fetch only bulb statuses
def fetch_bulb_status():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT bulb1, bulb2, bulb3 FROM StreetLightStatus ORDER BY id DESC LIMIT 1")
    status = cursor.fetchone()
    conn.close()
    return status

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

# Function to display bulb status with appropriate styling
def display_bulb_status(bulb_name, status):
    status = str(status).strip()  # Convert to string and remove whitespace
    if status == "0":
        st.error(f"🔴 {bulb_name}: OFF")
    elif status == "1":
        st.warning(f"🟡 {bulb_name}: Lower Watt Bulb ON")
    elif status == "2":
        st.success(f"🟢 {bulb_name}: Higher Watt Bulb ON")
    else:
        st.info(f"🔵 {bulb_name}: Unknown Status ({status})")

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
    
    status = fetch_bulb_status()
    
    if status:
        # Display each bulb's status with appropriate styling
        display_bulb_status("Bulb 1", status['bulb1'])
        display_bulb_status("Bulb 2", status['bulb2'])
        display_bulb_status("Bulb 3", status['bulb3'])
        
        # Add visual divider
        st.markdown("---")
        
        # Display status summary
        bulbs = [str(status['bulb1']).strip(), str(status['bulb2']).strip(), str(status['bulb3']).strip()]
        status_counts = {
            "OFF (0)": sum(1 for bulb in bulbs if bulb == "0"),
            "Lower Watt (1)": sum(1 for bulb in bulbs if bulb == "1"),
            "Higher Watt (2)": sum(1 for bulb in bulbs if bulb == "2"),
            "Unknown": sum(1 for bulb in bulbs if bulb not in ["0", "1", "2"])
        }
        
        st.subheader("📊 Status Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("OFF", status_counts["OFF (0)"])
        with col2:
            st.metric("Lower Watt", status_counts["Lower Watt (1)"])
        with col3:
            st.metric("Higher Watt", status_counts["Higher Watt (2)"])
        with col4:
            st.metric("Unknown", status_counts["Unknown"])
    else:
        st.warning("No bulb status data available")

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
