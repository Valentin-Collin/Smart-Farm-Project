#include <SoftwareSerial.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_I2CDevice.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <BH1750.h>
#include <Ultrasonic.h>
#include <HCSR04.h>

// Pin and sensor definitions
#define RE 8  // Pin for RS-485 Transmitter Enable
#define DE 7  // Pin for RS-485 Receiver Enable
#define moisturesensorPin A0  // Pin for soil moisture sensor
#define DHTPIN 4  // Pin for DHT sensor
#define DHTTYPE DHT22  // DHT sensor type (DHT22)

// Define RS-485 commands for nitrogen, phosphorous, and potassium sensors
const byte nitro[] = {0x01, 0x03, 0x00, 0x1e, 0x00, 0x01, 0xe4, 0x0c};
const byte phos[] = {0x01, 0x03, 0x00, 0x1f, 0x00, 0x01, 0xb5, 0xcc}; // Command to request phosphorous sensor data
const byte pota[] = {0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xc0}; // Command to request potassium sensor data

byte values[8];  // Array to store sensor response values
SoftwareSerial mod(2, 3);  // RS-485 communication using software serial on pins 2 (RX) and 3 (TX)

// Sensor initialization
UltraSonicDistanceSensor distanceSensor(13, 12);  // Ultrasonic sensor with digital pins 13 (trigger) and 12 (echo)
DHT dht(DHTPIN, DHTTYPE);  // DHT sensor for humidity and temperature
BH1750 lightMeter;  // Light sensor (BH1750)

// Variables for sensor data and calculations
float calibration_value = 21.34 - 0.3;  // Calibration value for pH sensor
int phval = 0; 
unsigned long avgval;
int buffer_arr[10], temp2;

void setup() {
  Serial.begin(9600);  // Start serial communication
  Wire.begin();  // Initialize I2C communication
  lightMeter.begin();  // Initialize BH1750 light sensor
  dht.begin();  // Initialize DHT sensor
  mod.begin(4800);  // Initialize RS-485 communication (software serial)
  
  // Set pins for RS-485 control
  pinMode(RE, OUTPUT);
  pinMode(DE, OUTPUT);
  
  delay(3000);  // Wait 3 seconds before starting main loop
}

void loop() {
  // Reading all sensor values
  uint16_t nitrogenValue = nitrogen();  // Nitrogen sensor value
  delay(500);
  uint16_t phosphorousValue = phosphorous();  // Phosphorous sensor value
  delay(500);
  uint16_t potassiumValue = potassium();  // Potassium sensor value
  delay(500);
  float soilHumidity = readSoilHumiditySensor();  // Soil moisture sensor value
  delay(2000);
  float hum = readHumiditySensor();  // Humidity sensor value
  delay(2000);
  float temp = dht.readTemperature();  // Temperature value from DHT sensor
  delay(500);
  float lux = readLightSensor();  // Light intensity value
  delay(500);
  float rain = readUltrasonicSensor();  // Rainfall (using ultrasonic sensor to measure water level)
  delay(500);
  float ph = readPhSensor();  // pH sensor value
  delay(500);

// Check for NaN (Not a Number) values and replace them with 0 if needed
  if (isnan(hum)) {
    hum = 0;
  }
  if (isnan(temp)) {
    temp = 0;
  }
  if (isnan(lux)) {
    lux = 0;
  }
  if (isnan(rain)) {
    rain = 0;
  }
  if (isnan(ph)) {
    ph = 0;
  }
  if (isnan(soilHumidity)) {
    soilHumidity = 0;
  }
  if (isnan(nitrogenValue)) {
    nitrogenValue = 0;
  }
  if (isnan(phosphorousValue)) {
    phosphorousValue = 0;
  }
  if (isnan(potassiumValue)) {
    potassiumValue = 0;
  }

  // Create JSON string to send sensor data
  String json = "{";
  json += "\"nitrogen\":" + String(nitrogenValue) + ",";
  json += "\"phosphorous\":" + String(phosphorousValue) + ",";
  json += "\"potassium\":" + String(potassiumValue) + ",";
  json += "\"soilHumidity\":" + String(soilHumidity) + ",";
  json += "\"humidity\":" + String(hum) + ",";
  json += "\"temperature\":" + String(temp) + ",";
  json += "\"light\":" + String(lux) + ",";
  json += "\"rainfall\":" + String(rain) + ",";
  json += "\"ph\":" + String(ph);
  json += "}";

  // Send JSON string over serial communication
  Serial.println(json);

  delay(500);  // Delay 0.5 seconds before next iteration
}

// Function to read sensor data via RS-485
uint16_t readSensorValue(const byte* command, const char* label) {
  for (int attempt = 0; attempt < 3; attempt++) {  // Try reading up to 3 times
    digitalWrite(DE, HIGH);  // Enable RS-485 transmission
    digitalWrite(RE, HIGH);
    delay(10);
    mod.write(command, 8);  // Send the sensor request command
    digitalWrite(DE, LOW);  // Disable RS-485 transmission
    digitalWrite(RE, LOW);

    delay(100);  // Wait for response

    if (mod.available() >= 7) {  // Check if enough data is available
      Serial.print(label);
      Serial.print(": ");
      for (byte i = 0; i < 7; i++) {
        if (mod.available()) {
          values[i] = mod.read();  // Read response data
          Serial.print(values[i], HEX);  // Print data in hexadecimal
          Serial.print(" ");
        }
      }
      Serial.println();

      // Combine the 3rd and 4th bytes to form a 16-bit value (sensor data)
      uint16_t combinedValue = (values[3] << 8) | values[4];
      Serial.print("Combined Value: ");
      Serial.print(combinedValue, HEX);  // Print in hexadecimal
      Serial.print(" = ");
      Serial.print(combinedValue);  // Print actual value
      Serial.println(" mg/kg");
      return combinedValue;  // Return the sensor value
    }
  }
  return 0;  // Return 0 if no data was read
}

// Functions for specific sensors
uint16_t nitrogen() {
  return readSensorValue(nitro, "Nitrogen");
}

uint16_t phosphorous() {
  return readSensorValue(phos, "Phosphorous");
}

uint16_t potassium() {
  return readSensorValue(pota, "Potassium");
}

float readSoilHumiditySensor() {
  int x = analogRead(moisturesensorPin);  // Read analog value from the soil moisture sensor
  // Polynomial formula to convert analog value to moisture percentage
  float outputValue = 127 + (0.431 * x) + (-2.28 * pow(10, -3) * pow(x, 2)) + (3.19 * pow(10, -6) * pow(x, 3)) + (-1.45 * pow(10, -9) * pow(x, 4));
  return outputValue;  // Return the calculated soil moisture value
}

float readHumiditySensor() {
  float hum = dht.readHumidity();  // Read humidity from DHT sensor
  float x = ((0.793 * hum) + 3.95);  // Adjust humidity value (calibration)
  return x;
}

float readLightSensor() {
  float lux = lightMeter.readLightLevel();  // Read light level from BH1750 sensor
  float x = ((1.02) * lux + 24.3);  // Adjust light value (calibration)
  return x;
}

float readUltrasonicSensor() {
  float distance = distanceSensor.measureDistanceCm();  // Measure distance in cm from ultrasonic sensor
  Serial.println(distance);
  float x = 30 - distance;  // Calculate water level (assume 30 cm max)
  if (x < 0) {
    x = 0;  // If below 0, set to 0
  }
  return distance;
}

float readPhSensor() {
  // Reading and averaging 10 pH sensor readings
  for (int i = 0; i < 10; i++) { 
    buffer_arr[i] = analogRead(A1);
    delay(30);
  }
  // Sorting the buffer values
  for (int i = 0; i < 9; i++) {
    for (int j = i + 1; j < 10; j++) {
      if (buffer_arr[i] > buffer_arr[j]) {
        temp2 = buffer_arr[i];
        buffer_arr[i] = buffer_arr[j];
        buffer_arr[j] = temp2;
      }  
    }
  }
  
  // Average the middle 6 values (after discarding the extremes)
  avgval = 0;
  for (int i = 2; i < 8; i++)
    avgval += buffer_arr[i];
  
  // Convert analog value to voltage
  float volt = (float)avgval * 5.0 / 1024 / 6;
  // Calculate pH based on voltage and calibration
  float ph_act = -5.70 * volt + calibration_value;

  Serial.println(ph_act);
  return ph_act;  // Return the pH value
}
