import streamlit as st
import mysql.connector
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# MySQL connection function
def get_connection():
    return mysql.connector.connect(
        host="82.180.143.66",
        user="u263681140_students",
        password="testStudents@123",
        database="u263681140_students"
    )


def fetch_dataBulb():
    connection = get_connection()
    query = "SELECT bulb1, bulb2, bulb3 FROM StreetLightStatus WHERE id = 1"
    df = pd.read_sql(query, connection)
    connection.close()
    return df
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

    #st.subheader("📊 Raw Data")
    #st.dataframe(df)

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
    
    df = fetch_dataBulb()
    #latest = df[df['id'] == 1].iloc[0]  # Fetch the row where id == 1
    latest = df.iloc[0]     
    def interpret_status(value):
        if str(value) == '0':
            return "🔴 Bulb is OFF"
        elif str(value) == '1':
            return "🟡 LowWatt Bulb is ON"
        elif str(value) == '2':
            return "🟢 HighWatt Bulb is ON"
        else:
            return "⚠️ Unknown Status"

    st.write("🔸 Bulb1 Status:", interpret_status(latest.get("bulb1", "Unknown")))
    st.write("🔸 Bulb2 Status:", interpret_status(latest.get("bulb2", "Unknown")))
    st.write("🔸 Bulb3 Status:", interpret_status(latest.get("bulb3", "Unknown")))
    
def date_management_tab():
    st.title("🗓️ Manage Data by Date")

    df = fetch_data()


    # Radio button for action
    action = st.radio("Select Action", ["Show Raw Data", "Delete Selected Data"])

    # Date inputs
    st.subheader("📅 Select Date Range")
    col1, col2 = st.columns(2)
    # Get min/max available dates
    min_date = df['only_date'].min()
    max_date = df['only_date'].max()
    to_date = st.date_input("To Date", min_value=min_date, max_value=max_date, value=max_date)

    with col1:
        from_date = st.date_input("From Date", min_value=min_date, max_value=max_date, value=min_date)
    with col2:
        
        # Ensure 'DateTime' is parsed as datetime and extract just the date
        df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce')
        df['only_date'] = df['DateTime'].dt.date
    
 
    if from_date > to_date:
        st.warning("⚠️ 'From Date' must be earlier than or equal to 'To Date'")
        return

    # Filter DataFrame based on selected date range
    mask = (df['only_date'] >= from_date) & (df['only_date'] <= to_date)
    filtered_df = df.loc[mask]

    if action == "Show Raw Data":
        st.subheader("📊 Filtered Data")
        st.dataframe(filtered_df)

    elif action == "Delete Selected Data":
        
        st.warning("⚠️ This will permanently delete data in the selected range.")
        if st.button("❌ Confirm Deletion"):
            conn = get_connection()
            cursor = conn.cursor()
            delete_query = "DELETE FROM StreetLight WHERE DATE(DateTime) BETWEEN %s AND %s"
            cursor.execute(delete_query, (from_date, to_date))
            conn.commit()
            conn.close()
            st.success("✅ Data deleted successfully!")
# Main app with tabs
def main_app():
    # Auto-refresh every 5 seconds (5000 milliseconds)
    st_autorefresh(interval= 10000, limit=None, key="auto-refresh")

    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "💡 Bulb Status", "🗓️ Manage by Date"])
    
    with tab1:
        dashboard()
    
    with tab2:
        bulb_status()
    with tab3:
        
        #df = fetch_data()
    
        
        date_management_tab()

        

# Entry point
if not st.session_state.logged_in:
    login()
else:
    main_app()
