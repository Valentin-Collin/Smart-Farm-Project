import streamlit as st
import pandas as pd
import altair as alt
import sys
import mariadb
import pickle as pk
import sklearn.metrics as metrics
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import datetime
import base64

from streamlit_autorefresh import st_autorefresh
from sqlalchemy import create_engine, text
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

# Automatically refresh the Streamlit app every 60 seconds
count = st_autorefresh(interval=60000, limit=10000, key="fizzbuzzcounter")

# Try to connect to the MariaDB database; exit with an error message if it fails
try:
    baseDeDonnees = mariadb.connect(
        host="localhost",
        user="root",
        password="root",
        database="SmartFarm"
    )

except mariadb.Error as error:
    print(f"Error connecting to MariaDB Platform: {error}")
    sys.exit(1)

# Create a cursor for executing SQL queries
cursor = baseDeDonnees.cursor()

# Function to retrieve the latest values from various sensor data tables
def get_latest_values(cursor):
    # List of sensor data tables
    tables = ['nitrogen_data', 'phosphorous_data', 'potassium_data', 
              'soil_humidity_data', 'humidity_data', 'temperature_data', 
              'light_data', 'rainfall_data', 'ph_data']
    latest_values = {}
    # Loop through each table and get the latest value
    for table in tables:
        query = f"SELECT Sensor_ID, Date, Time, Value FROM {table} ORDER BY Date DESC, Time DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()
        latest_values[table] = result
    # Print the latest values for debugging purposes
    for i in latest_values.items():    
        print(i)
    return latest_values

# Function to retrieve the last 360 values from a specified table
def get_last_360_values(cursor, table_name):
    query = f"SELECT Date, CAST(Time AS DATETIME) AS Time, Value FROM {table_name} ORDER BY Date DESC, Time DESC LIMIT 360"
    cursor.execute(query)
    result = cursor.fetchall()
    # Create a DataFrame from the fetched results
    df = pd.DataFrame(result, columns=['Date', 'Time', 'Value'])
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.time
    df['Datetime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str), format='%Y-%m-%d %H:%M:%S')

    # Round values for specific tables
    if table_name in ["nitrogen_data", "phosphorous_data", "potassium_data"]:
        df['Value'] = df['Value'].astype(float).apply(lambda x: round(x, 1))

    # Print the DataFrame for debugging
    print(f"DataFrame for {table_name}:\n{df.head()}")
    
    return df

# Function to retrieve values from a specified table based on the selected time period
def get_last_values(period, cursor, table_name):
    now = datetime.datetime.now()
    # Define time intervals for filtering the data
    Lastminute = now - datetime.timedelta(seconds=60)
    Lasthour = now - datetime.timedelta(hours=1)
    Lastday = now - datetime.timedelta(days=1)
    Lastmonth = now - datetime.timedelta(weeks=4)

    # SQL query construction based on the specified period
    if period == "Last minute":
        query = f"""
            SELECT Date, CAST(Time AS DATETIME) AS Time, Value 
            FROM {table_name} 
            WHERE Date >= '{Lastminute.strftime('%Y-%m-%d')}' AND Time >= '{Lastminute.strftime('%H:%M:%S')}'
            ORDER BY Date DESC, Time DESC
        """
    elif period == "Last hour":
        query = f"""
            SELECT Date, CAST(Time AS DATETIME) AS Time, Value 
            FROM {table_name} 
            WHERE Date >= '{Lasthour.strftime('%Y-%m-%d')}' AND Time >= '{Lasthour.strftime('%H:%M:%S')}'
            ORDER BY Date DESC, Time DESC
        """
    elif period == "Last day":
        query = f"""
            SELECT Date, CAST(Time AS DATETIME) AS Time, Value 
            FROM {table_name} 
            WHERE Date >= '{Lastday.strftime('%Y-%m-%d')}'
            ORDER BY Date DESC, Time DESC
        """
    elif period == "Last month":
        query = f"""
            SELECT Date, CAST(Time AS DATETIME) AS Time, Value 
            FROM {table_name} 
            WHERE Date >= '{Lastmonth.strftime('%Y-%m-%d')}'
            ORDER BY Date DESC, Time DESC
        """
    else:
        query = f"""
            SELECT Date, CAST(Time AS DATETIME) AS Time, Value 
            FROM {table_name} 
            WHERE Date >= '{Lastmonth.strftime('%Y-%m-%d')}' AND Time >= '{Lastmonth.strftime('%H:%M:%S')}'
            ORDER BY Date DESC, Time DESC
        """
    
    cursor.execute(query)
    result = cursor.fetchall()
    # Create a DataFrame from the fetched results
    df = pd.DataFrame(result, columns=['Date', 'Time', 'Value'])
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.time
    df['Datetime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str), format='%Y-%m-%d %H:%M:%S')

    # Print the DataFrame for debugging
    print(df)
    return df

# Function to test get_last_values with different time periods
def test_get_last_values():
    periods = ["Last minute", "Last hour", "Last day", "Last month"]
    table_name = 'nitrogen_data'
    
    # Loop through each period and print the results
    for period in periods:
        print(f"\nTesting '{period}':")
        df = get_last_values(period, cursor, table_name)
        print(df.head())

# Execute the test function
test_get_last_values()

# Function to encode an image as a base64 string for use in Streamlit
def get_base64_image(path):
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return f'data:image/jpg;base64,{encoded_string}'




# Streamlit interface
st.title('Sensor Data Dashboard')

# Define units for each sensor data
units = {
    "nitrogen_data": "mg/kg",
    "phosphorous_data": "mg/kg",
    "potassium_data": "mg/kg",
    "soil_humidity_data": "%",
    "humidity_data": "%",
    "temperature_data": "°C",
    "light_data": "lux",
    "rainfall_data": "mm"
}

# Dictionary to map sensor types to their images
sensor_images = {
    "nitrogen_data": r"C:\Users\valen\Pictures\nitrogen_image.jpg",
    "phosphorous_data": r"C:\Users\valen\Pictures\phosphorous_image.jpg",
    "potassium_data": r"C:\Users\valen\Pictures\potassium_image.jpg",
    "soil_humidity_data": r"C:\Users\valen\Pictures\soil_humidity_image.jpg",
    "humidity_data": r"C:\Users\valen\Pictures\humidity_image.png",
    "temperature_data": r"C:\Users\valen\Pictures\temperature_image.jpg",
    "light_data": r"C:\Users\valen\Pictures\light_image.png",
    "rainfall_data": r"C:\Users\valen\Pictures\rainfall_image.jpg",
    "ph_data": r"C:\Users\valen\Pictures\ph_image.png"
}

# Display the latest sensor values
st.header('Latest Sensor Values')
latest_values = get_latest_values(cursor)  # Fetch latest sensor values from the database

for param, value in latest_values.items():
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"**{param.replace('_data', '').capitalize()}**")
    with col2:
        if value:
            unit = units.get(param, "")
            st.markdown(f"""
                <div style="border: 2px solid #4CAF50; padding: 10px; border-radius: 5px; background-color: #f9f9f9; margin-bottom: 0 px;">
                    <img src="{get_base64_image(sensor_images[param])}" style="float: right; margin-left: 10px; padding-right: 10px; max-width: 100%;" width="100">
                    <span style="color: #4CAF50;"><b>Sensor:</b> {value[0]}</span><br>
                    <span><b>Date:</b> {value[1]}</span><br>
                    <span><b>Time:</b> {value[2]}</span><br>
                    <span><b>Value:</b> {value[3]} {unit}</span><br>
                    
                </div>
            """, unsafe_allow_html=True)
        else:
            unit = units.get(param, "")
            st.markdown(f"""
                <div style="border: 2px solid #4CAF50; padding: 10px; border-radius: 5px; background-color: #f9f9f9; margin-bottom: 0 px;">
                    <img src="{get_base64_image(sensor_images[param])}" style="float: right; margin-left: 10px; padding-right: 10px; max-width: 100%;" width="100">
                    <span style="color: #4CAF50;"><b>Sensor:</b></span><br>
                    <span><b>Date:</b> No data available </span><br>
                    <span><b>Time:</b> No data available </span><br>
                    <span><b>Value:</b> No data available </span><br>
                    
                </div>
            """, unsafe_allow_html=True)

# Section for parameter visualization
st.title('Parameters as a function of time')
st.header("Select a Period")

# Options for selection
options = ["Last minute", "Last hour", "Last day", "Last month"]
period = "Last month"  # Default period
# Dropdown for selecting period
period = st.selectbox("Select a period:", options)

# Display the selected option
st.write(f"You have selected: {period}")

# Generate and display charts for each parameter
for table in latest_values.keys():
    st.subheader(f"{table.replace('_data', '').capitalize()}")
    df = get_last_values(period, cursor, table)
    if not df.empty:

        if (period =="Last minute"):
            df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S')

            chart = alt.Chart(df).mark_line(point=True).encode(
                alt.X('Time:T', axis=alt.Axis(
                grid=True, 
                title='Time',
                format='%H:%M:%S' 
                )),
                alt.Y('Value:Q', axis=alt.Axis(grid=True), title='Value'),
                tooltip=['Time:T', 'Value:Q']
            ).properties(
                width='container',
                height=400
            ).configure_axis(
                titleFontSize=16,
                labelFontSize=16,
                labelAngle=-45
            ).configure_view(
                strokeWidth=0
            )
            # Display chart in Streamlit
            st.altair_chart(chart, use_container_width=True)

        else:
            df['Datetime'] = pd.to_datetime(df['Datetime'])
            
            chart = alt.Chart(df).mark_line(point=True).encode(
                alt.X('Datetime:T', type='temporal', axis=alt.Axis(grid=True), title='Time'),
                alt.Y('Value:Q', axis=alt.Axis(grid=True), title='Value'),
                tooltip=['Datetime:T', 'Value:Q']
            ).properties(
                width='container',
                height=400
            ).configure_axis(
                titleFontSize=16,
                labelFontSize=16,
                labelAngle=-45
            ).configure_view(
                strokeWidth=0
            )
            # Display chart in Streamlit
            st.altair_chart(chart, use_container_width=True)
    else:
        st.write("No data available")

# Section for crop recommendations
st.header('Crop Recommendation')

# List of parameters for input
ListeParamètres = ['N (mg/kg)', 'P (mg/kg)', 'K (mg/kg)', 'Temperature (°C)', 'Humidity (%)', 'Ph', 'Rainfall (mm)']
ListeValeur = []

# Collecting parameter values through text input boxes
for index, element in enumerate(ListeParamètres):
    valeur = st.text_input(element, key=f"input_{index}")
    ListeValeur.append(valeur)

# Function for crop recommendation
def CropRecommendation(ListeValeur):
    # Create a DataFrame from the formatted values
    data = pd.DataFrame([ListeValeur], columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])

    # Select the corresponding feature columns
    features = data[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]

    # Path to the saved model
    filename = 'LogisticRegresion.pkl'
    MODELS = 'C:/Users/valen/Desktop/SmartFarm/'

    # Load the saved model
    model = pk.load(open(MODELS + filename, 'rb'))

    # Make a prediction using the model
    CropRecommendationResult = model.predict(features)
    st.success(f"It is recommended to grow: {CropRecommendationResult[0]}")

    return CropRecommendationResult[0]

# Button to initiate crop recommendation
if st.button('Crop Recommendation'):
    recommendation = CropRecommendation(ListeValeur)
    st.text_area("Result", recommendation)

# Close the database connection at the end
baseDeDonnees.close()


