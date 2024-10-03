import serial  # For serial communication with Arduino
import time  # For delay and time management
import mariadb  # For MariaDB database connection
import sys  # For system exit
import json  # For handling JSON data
from datetime import datetime  # For managing date and time

# Connect to the MariaDB database
try:
    baseDeDonnees = mariadb.connect(
        host="localhost",  # Database server
        user="root",       # Database user
        password="root",   # Database password
        database="SmartFarm"  # Name of the database
    )
except mariadb.Error as error:
    print(f"Error connecting to MariaDB Platform: {error}")
    sys.exit(1)

# Create a cursor to interact with the database
cursor = baseDeDonnees.cursor()

# Function to insert data into respective tables
def insert_data(sensor_id, value, table_name):
    now = datetime.now()  # Get current date and time
    date_str = now.strftime('%Y-%m-%d')  # Format the date
    time_str = now.strftime('%H:%M:%S')  # Format the time
    try:
        # SQL query to insert sensor data
        sql = f"INSERT INTO {table_name} (Sensor_ID, Date, Time, Value) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (sensor_id, date_str, time_str, value))
        baseDeDonnees.commit()  # Commit the transaction to save the data
        print(f"Data inserted into {table_name} successfully")
    except mariadb.Error as error:
        print(f"Error: {error}")  # Handle SQL errors
        baseDeDonnees.rollback()  # Rollback the transaction on failure

# Main code block for communication with Arduino
if __name__ == '__main__':
    # Setup serial communication (check the correct port for Arduino)
    ser = serial.Serial('/dev/ttyUSB5', 9600, timeout=1)
    ser.reset_input_buffer()  # Clear any existing input

    while True:
        ser.write(b"Hello from Raspberry Pi!\n")  # Send a message to Arduino
        line = ser.readline().decode('utf-8').rstrip()  # Read incoming data

        if line:  # If data is received
            print("Received:", line)
            if line.startswith('{') and line.endswith('}'):  # Check if data is JSON
                try:
                    data = json.loads(line)  # Parse the JSON data
                    # Insert data into respective tables
                    insert_data(1, data['nitrogen'], 'nitrogen_data')
                    insert_data(2, data['phosphorous'], 'phosphorous_data')
                    insert_data(3, data['potassium'], 'potassium_data')
                    insert_data(4, data['soilHumidity'], 'soil_humidity_data')
                    insert_data(5, data['humidity'], 'humidity_data')
                    insert_data(6, data['temperature'], 'temperature_data')
                    insert_data(7, data['light'], 'light_data')
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")  # Handle JSON parsing errors
            else:
                print("Invalid data format received")  # Handle non-JSON data
        
        time.sleep(0.1)  # Wait for a short time before the next loop

# Close the database connection when the program finishes
baseDeDonnees.close()
