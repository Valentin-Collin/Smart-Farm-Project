import tkinter as tk
import serial
import json
import time

# Configure the serial connection (adjust according to your setup)
arduino = serial.Serial('COM3', 9600, timeout=None)  # Replace 'COM3' with the appropriate port

def send_command(command):
    command = command + '\n'  # Add a newline character at the end of the command
    arduino.write(command.encode())  # Send the command to the Arduino
    time.sleep(1)  # Wait a moment for the Arduino to process the command

def receive_data():
    # Read a line of data from the Arduino
    data = arduino.readline().decode().strip()  # Decode and strip any whitespace
    print(f"Received data: {data}")  # Print received data for debugging
    
    # Try to decode the JSON data
    try:
        data_dict = json.loads(data)  # Load the JSON data into a dictionary
        voltage = float(data_dict.get("Voltage", 0))  # Get voltage value
        analogue_value = float(data_dict.get("Analogue Value", 0))  # Get analogue value
        absorbance = float(data_dict.get("Absorbance", 0))  # Get absorbance value
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Data conversion error: {e}")  # Print error message if conversion fails
        voltage = analogue_value = absorbance = 0.0  # Default to 0.0 on error

    return voltage, analogue_value, absorbance  # Return the sensor values

def update_labels():
    # Retrieve data from the Arduino
    voltage, analogue_value, absorbance = receive_data()

    # Update the labels with the new values, formatted to two decimal places
    voltage_label.config(text=f"Voltage: {voltage:.2f} V")
    analogue_value_label.config(text=f"Analog value: {analogue_value:.2f}")
    absorbance_label.config(text=f"Absorbance: {absorbance:.2f}")

    # Repeat the update after 1000 ms (1 second)
    root.after(1000, update_labels)

def on_color_change(color):
    send_command(color)  # Send the color command to the Arduino
    
    # Update the nutrient label based on the selected color
    if color == 'red':
        nutrient_label.config(text="Nutrient: Potassium")  # Red indicates Potassium
    elif color == 'green':
        nutrient_label.config(text="Nutrient: Phosphorus")  # Green indicates Phosphorus
    elif color == 'blue':
        nutrient_label.config(text="Nutrient: Nitrogen")  # Blue indicates Nitrogen
    elif color == 'none':
        nutrient_label.config(text="Nutrient: None")  # No color indicates no nutrient

# Create an instance of the main window
root = tk.Tk()
root.title("Optical NPK Sensor")  # Set the window title

# Create color buttons
tk.Button(root, text="Red", command=lambda: on_color_change('red')).pack(pady=5)
tk.Button(root, text="Green", command=lambda: on_color_change('green')).pack(pady=5)
tk.Button(root, text="Blue", command=lambda: on_color_change('blue')).pack(pady=5)
tk.Button(root, text="None", command=lambda: on_color_change('none')).pack(pady=5)

# Create labels to display sensor values
voltage_label = tk.Label(root, text="Voltage: ")
voltage_label.pack()

analogue_value_label = tk.Label(root, text="Analog value: ")
analogue_value_label.pack()

absorbance_label = tk.Label(root, text="Absorbance: ")
absorbance_label.pack()

# Create a label to display the type of nutrient
nutrient_label = tk.Label(root, text="Nutrient: ")
nutrient_label.pack()

# Start updating the labels with sensor data
update_labels()

# Run the main loop
root.mainloop()

arduino.close()  # Close the serial connection when the program ends
