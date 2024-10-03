-- Drop temperature readings table
-- DROP TABLE temperature_data;
-- Drop humidity readings table
-- DROP TABLE humidity_data;
-- Drop nitrogen readings table
-- DROP TABLE nitrogen_data;
-- Drop phosphorus readings table
-- DROP TABLE phosphorous_data;sensorssensors
-- Drop potassium readings table
-- DROP TABLE potassium_data;
-- Drop illuminance readings table
-- DROP TABLE light_data ;S
-- Drop sensors table
-- DROP TABLE Sensors;
-- DROP TABLE soil_humidity_data ;
-- Sensors table

CREATE TABLE Sensors (
    Sensor_ID INT PRIMARY KEY,
    Sensor_Name VARCHAR(50)
);

CREATE TABLE nitrogen_data (
    
    Sensor_ID INT,
    Date DATE,
    Time TIME,
    Value FLOAT,
    FOREIGN KEY (Sensor_ID) REFERENCES Sensors(Sensor_ID)
);

CREATE TABLE phosphorous_data (
	
    Sensor_ID INT,
    Date DATE,
    Time TIME,
    Value FLOAT,
    FOREIGN KEY (Sensor_ID) REFERENCES Sensors(Sensor_ID)
);

CREATE TABLE potassium_data (
	
    Sensor_ID INT,
    Date DATE,
    Time TIME,
    Value FLOAT,
    FOREIGN KEY (Sensor_ID) REFERENCES Sensors(Sensor_ID)
);

CREATE TABLE soil_humidity_data (
	
    Sensor_ID INT,
    Date DATE,
    Time TIME,
    Value FLOAT,
    FOREIGN KEY (Sensor_ID) REFERENCES Sensors(Sensor_ID)
);

CREATE TABLE humidity_data (
	
    Sensor_ID INT,
    Date DATE,
    Time TIME,
    Value FLOAT,
    FOREIGN KEY (Sensor_ID) REFERENCES Sensors(Sensor_ID)
);

CREATE TABLE temperature_data (

    Sensor_ID INT,
    Date DATE,
    Time TIME,
    Value FLOAT,
    FOREIGN KEY (Sensor_ID) REFERENCES Sensors(Sensor_ID)
);

CREATE TABLE light_data (
	
    Sensor_ID INT,
    Date DATE,
    Time TIME,
    Value FLOAT,
    FOREIGN KEY (Sensor_ID) REFERENCES Sensors(Sensor_ID)
);

CREATE TABLE rainfall_data (
	
    Sensor_ID INT,
    Date DATE,
    Time TIME,
    Value FLOAT,
    FOREIGN KEY (Sensor_ID) REFERENCES Sensors(Sensor_ID)
);

CREATE TABLE ph_data (
	
    Sensor_ID INT,
    Date DATE,
    Time TIME,
    Value FLOAT,
    FOREIGN KEY (Sensor_ID) REFERENCES Sensors(Sensor_ID)
);
