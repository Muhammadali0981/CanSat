#include "Wire.h"
#include <MPU6050_light.h>
#include <Adafruit_BMP280.h>
#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>
#include <ArduinoJson.h>

// MPU6050 and BMP280 objects
MPU6050 mpu(Wire);
Adafruit_BMP280 bmp; // I2C

// GPS settings
static const int GPS_RXPin = 4, GPS_TXPin = 3;
static const uint32_t GPSBaud = 9600;

// HC-12 settings
static const int HC12_TXPin = 10, HC12_RXPin = 11;
static const uint32_t HC12Baud = 9600;

// TinyGPSPlus object and SoftwareSerial setup for GPS
TinyGPSPlus gps;
SoftwareSerial gpsSerial(GPS_RXPin, GPS_TXPin);

// HC-12 SoftwareSerial setup
SoftwareSerial hc12Serial(HC12_TXPin, HC12_RXPin);

unsigned long timer = 0;

void setup() {
  Serial.begin(9600);
  Wire.begin();

  // Initialize MPU6050
  byte status = mpu.begin();
  Serial.print(F("MPU6050 status: "));
  Serial.println(status);
  while (status != 0) { } // stop everything if could not connect to MPU6050
  
  Serial.println(F("Calculating offsets, do not move MPU6050"));
  delay(1000);
  mpu.upsideDownMounting = true; // uncomment this line if the MPU6050 is mounted upside-down
  mpu.calcOffsets(); // gyro and accelero
  Serial.println("Done!\n");
  
  // Initialize BMP280
  if (!bmp.begin(0x76)) {  // Specify the I2C address
    Serial.println("Could not find a valid BMP280 sensor, check wiring!");
    while (1);  // Stop if sensor is not found
  }
  Serial.println("BMP280 sensor detected.");

  // Initialize GPS
  gpsSerial.begin(GPSBaud);
  delay(1000);  // Give the GPS module time to start up
  Serial.println(F("GPS module initialized."));

  // Initialize HC-12
  hc12Serial.begin(HC12Baud);
  Serial.println(F("HC-12 module initialized."));
}

void loop() {
  // Process GPS data
  while (gpsSerial.available() > 0) {
    char c = gpsSerial.read();
    gps.encode(c);
  }

  // Update data every second
  if ((millis() - timer) > 1000) {
    updateMPU6050();
    updateBMP280();
    displayGPSInfo();  // Ensure GPS data is sent regularly

    // Update timer
    timer = millis();
  }
}

void updateMPU6050() {
  mpu.update();
  
  // Read MPU6050 data
  float Yaw = mpu.getAngleZ();
  float Pitch = mpu.getAngleX();
  float Roll = mpu.getAngleY();
  
  // Create JSON object
  StaticJsonDocument<256> doc;
  doc["yaw"] = Yaw;
  doc["pitch"] = Pitch;
  doc["roll"] = Roll;

  // Serialize JSON to string and send
  String output;
  serializeJson(doc, output);
  sendData(output);
}

void updateBMP280() {
  // Read BMP280 data
  float temperature = bmp.readTemperature();
  float pressure = bmp.readPressure();
  float altitude = bmp.readAltitude(1013.25); // Assumes standard sea level pressure
  
  // Create JSON object
  StaticJsonDocument<256> doc;
  doc["temperature"] = temperature;
  doc["pressure"] = pressure;
  doc["altitude"] = altitude;

  // Serialize JSON to string and send
  String output;
  serializeJson(doc, output);
  sendData(output);
}

void displayGPSInfo() {
  StaticJsonDocument<256> doc;

  // Add location data
  if (gps.location.isValid()) {
    doc["location"] = String(gps.location.lat(), 6) + "," + String(gps.location.lng(), 6);
  } else {
    doc["location"] = "INVALID";
  }

  // Add date data
  if (gps.date.isValid()) {
    doc["date"] = String(gps.date.month()) + "/" + String(gps.date.day()) + "/" + String(gps.date.year());
  } else {
    doc["date"] = "INVALID";
  }

  // Add time data
  if (gps.time.isValid()) {
    char timeBuffer[10];
    sprintf(timeBuffer, "%02d:%02d:%02d", gps.time.hour(), gps.time.minute(), gps.time.second());
    doc["time"] = timeBuffer;
  } else {
    doc["time"] = "INVALID";
  }

  // Serialize JSON to string and send
  String output;
  serializeJson(doc, output);
  sendData(output);
}

void sendData(const String &data) {
  Serial.println(data); // Print to Serial Monitor
  hc12Serial.println(data); // Send the data string via HC-12
}
