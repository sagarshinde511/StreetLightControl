import plotly.graph_objects as go

def main():
    st.title("💡 Street Light Monitoring System")

    df = fetch_data()

    st.subheader("📊 Raw Data")
    st.dataframe(df)

    # Choose what to visualize
    option = st.selectbox("Select parameter to visualize", ["Current", "Voltage"])

    if option == "Current":
        labels = ['Current1', 'Current2', 'Current3']
    else:
        labels = ['Vtg1', 'Vtg2', 'Vtg3']

    # Get latest row (or average/sum if you prefer)
    latest = df.iloc[-1]  # last row

    # Raw display values with units
    display_labels = [f"{col}: {latest[col]}" for col in labels]

    # Numeric values for plotting
    numeric_values = latest[labels].replace('[^0-9.]', '', regex=True).astype(float)

    fig = go.Figure(data=[go.Pie(
        labels=display_labels,
        values=numeric_values,
        textinfo='label+percent',
        hoverinfo='label+value'
    )])

    fig.update_layout(title="Distribution of " + option)

    st.plotly_chart(fig)
