// Pin assignments for the RGB LED
int redpin = 11;    // Pin for the red LED
int bluepin = 9;    // Pin for the blue LED
int greenpin = 10;  // Pin for the green LED

// Constants for absorbance calculation
float I0 = 1023;    // Reference light intensity (max analog value)
int photoresistor = A0; // Pin for the photoresistor

// Variables for sensor readings and calculations
int photoresistorvalue; // Value read from the photoresistor
float voltage;          // Calculated voltage from the photoresistor
float absorbance;      // Calculated absorbance based on light intensity
int numReadings = 100; // Number of readings for averaging

// Command string received from Serial
String command;

void setup() {
    Serial.begin(9600);        // Initialize Serial communication at 9600 baud rate
    pinMode(redpin, OUTPUT);   // Set the red LED pin as an output
    pinMode(bluepin, OUTPUT);  // Set the blue LED pin as an output
    pinMode(greenpin, OUTPUT); // Set the green LED pin as an output

    // Initialize with the red light on
    redlight();
}

void loop() {
    // Check if there are any commands received via Serial
    if (Serial.available() > 0) {
        command = Serial.readStringUntil('\n'); // Read command until newline
        command.trim(); // Trim whitespace from the command

        // Change LED color based on the received command
        if (command == "red") {
            redlight();
        } 
        else if (command == "green") {
            greenlight();
        }
        else if (command == "blue") {
            bluelight();
        }
        else if (command == "blueovergreen") {
            blueovergreen();
        }
        else if (command == "blueoverred") {
            blueoverred();
        }
        else if (command == "greenoverred") {
            greenoverred();
        }
        else if (command == "none") {
            nonelight();
        }
    }
    
    // Measure the sensor values
    measureSensor();
    delay(500); // Delay between sensor readings

    // Send sensor data to the Serial monitor
    sendData();
    
    delay(100); // Additional delay before the next loop iteration
}

// Function to turn on the red LED
void redlight() {
    analogWrite(redpin, 255);   // Turn on red LED
    analogWrite(greenpin, 0);   // Turn off green LED
    analogWrite(bluepin, 0);    // Turn off blue LED
}

// Function to turn on the green LED
void greenlight() {
    analogWrite(redpin, 0);     // Turn off red LED
    analogWrite(greenpin, 255); // Turn on green LED
    analogWrite(bluepin, 0);    // Turn off blue LED
}

// Function to turn on the blue LED
void bluelight() {
    analogWrite(redpin, 0);     // Turn off red LED
    analogWrite(greenpin, 0);   // Turn off green LED
    analogWrite(bluepin, 255);  // Turn on blue LED
}

// Function to turn on blue LED over green
void blueovergreen() {
    analogWrite(redpin, 0);     // Turn off red LED
    analogWrite(greenpin, 255); // Turn on green LED
    analogWrite(bluepin, 255);  // Turn on blue LED
}

// Function to turn on blue LED over red
void blueoverred() {
    analogWrite(redpin, 255);   // Turn on red LED
    analogWrite(greenpin, 0);   // Turn off green LED
    analogWrite(bluepin, 255);  // Turn on blue LED
}

// Function to turn on green LED over red
void greenoverred() {
    analogWrite(redpin, 255);   // Turn on red LED
    analogWrite(greenpin, 255); // Turn on green LED
    analogWrite(bluepin, 0);    // Turn off blue LED
}

// Function to turn off all LEDs
void nonelight() {
    analogWrite(redpin, 0);     // Turn off red LED
    analogWrite(greenpin, 0);   // Turn off green LED
    analogWrite(bluepin, 0);    // Turn off blue LED
}

// Function to measure the photoresistor value
void measureSensor() {
    long total = 0; // Variable to hold the sum of readings
    
    // Take multiple readings and accumulate the total
    for (int i = 0; i < numReadings; i++) {
        total += analogRead(photoresistor); // Read the photoresistor value
        delay(50); // Delay between readings for stability
    }

    // Calculate the average reading
    photoresistorvalue = total / numReadings;

    // Calculate voltage and absorbance based on the average reading
    voltage = (photoresistorvalue / 1024.0) * 5; // Calculate voltage (0-5V)
    absorbance = -log10(photoresistorvalue / I0); // Calculate absorbance
}

// Function to send sensor data in JSON format
void sendData() {
    String json = "{";
    json += "\"Voltage\":" + String(voltage) + ","; // Add voltage to JSON
    json += "\"Analogue Value\":" + String(photoresistorvalue) + ","; // Add photoresistor value
    json += "\"Absorbance\":" + String(absorbance) + ","; // Add absorbance

    // Set a default value for "Color" if no command was received
    if (command == "") {
        command = "none"; // Default value for color
    }

    json += "\"Color\":\"" + command + "\""; // Add color to JSON
    json += "}"; 
    Serial.println(json); // Send JSON data to Serial monitor
}
