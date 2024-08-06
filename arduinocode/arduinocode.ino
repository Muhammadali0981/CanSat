#include "Wire.h"
#include <MPU6050_light.h>
#include <Adafruit_BMP280.h>
#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>

// MPU6050 and BMP280 objects
MPU6050 mpu(Wire);
Adafruit_BMP280 bmp; // I2C

// GPS settings
static const int GPS_RXPin = 3, GPS_TXPin = 4;
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
  Serial.println(F("GPS module initialized."));

  // Initialize HC-12
  hc12Serial.begin(HC12Baud);
  Serial.println(F("HC-12 module initialized."));
}

void loop() {
  // Process GPS data continuously
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }

  // Update MPU6050 and BMP280 data every second
  if ((millis() - timer) > 1000) { // print data every 1000ms (1 second)
    Serial.println("\n");
    String dataToSend = "";
    updateMPU6050(dataToSend);
    updateBMP280(dataToSend);
    displayGPSInfo(dataToSend);

    // Send data via HC-12
    sendDataViaHC12(dataToSend);

    // Update timer
    timer = millis();
  }
}

void updateMPU6050(String &dataToSend) {
  mpu.update();
  
  // Read and print MPU6050 data
  float Yaw = mpu.getAngleZ();
  float Pitch = mpu.getAngleX();
  float Roll = mpu.getAngleY();
  
  Serial.print("Yaw: ");
  Serial.print(Yaw);
  Serial.print("  Pitch: ");
  Serial.print(Pitch);
  Serial.print("  Roll: ");
  Serial.println(Roll);
  
  // Append data to string for HC-12 transmission
  dataToSend += "Yaw: " + String(Yaw) + " Pitch: " + String(Pitch) + " Roll: " + String(Roll) + " ";
}

void updateBMP280(String &dataToSend) {
  // Read and print BMP280 data
  float temperature = bmp.readTemperature();
  float pressure = bmp.readPressure();
  float altitude = bmp.readAltitude(1013.25); // Assumes standard sea level pressure
  
  Serial.print("Temperature = ");
  Serial.print(temperature);
  Serial.println(" degrees Celsius");

  Serial.print("Pressure = ");
  Serial.print(pressure);
  Serial.println(" Pa");

  Serial.print("Altitude = ");
  Serial.print(altitude);
  Serial.println(" m");

  // Append data to string for HC-12 transmission
  dataToSend += "Temperature: " + String(temperature) + " Pressure: " + String(pressure) + " Altitude: " + String(altitude) + " ";
}

void displayGPSInfo(String &dataToSend) {
  Serial.print(F("Location: ")); 
  if (gps.location.isValid()) {
    Serial.print(gps.location.lat(), 6);
    Serial.print(F(","));
    Serial.print(gps.location.lng(), 6);
    dataToSend += "Location: " + String(gps.location.lat(), 6) + "," + String(gps.location.lng(), 6) + " ";
  } else {
    Serial.print(F("INVALID"));
    dataToSend += "Location: INVALID ";
  }

  Serial.print(F("  Date/Time: "));
  if (gps.date.isValid()) {
    Serial.print(gps.date.month());
    Serial.print(F("/"));
    Serial.print(gps.date.day());
    Serial.print(F("/"));
    Serial.print(gps.date.year());
    dataToSend += "Date: " + String(gps.date.month()) + "/" + String(gps.date.day()) + "/" + String(gps.date.year()) + " ";
  } else {
    Serial.print(F("INVALID"));
    dataToSend += "Date: INVALID ";
  }

  Serial.print(F(" "));
  if (gps.time.isValid()) {
    if (gps.time.hour() < 10) Serial.print(F("0"));
    Serial.print(gps.time.hour());
    Serial.print(F(":"));
    if (gps.time.minute() < 10) Serial.print(F("0"));
    Serial.print(gps.time.minute());
    Serial.print(F(":"));
    if (gps.time.second() < 10) Serial.print(F("0"));
    Serial.print(gps.time.second());
    Serial.print(F("."));
    if (gps.time.centisecond() < 10) Serial.print(F("0"));
    Serial.print(gps.time.centisecond());
    dataToSend += "Time: " + String(gps.time.hour()) + ":" + String(gps.time.minute()) + ":" + String(gps.time.second()) + "." + String(gps.time.centisecond()) + " ";
  } else {
    Serial.print(F("INVALID"));
    dataToSend += "Time: INVALID ";
  }

  Serial.println();
}

void sendDataViaHC12(const String &data) {
  hc12Serial.println(data); // Send the data string via HC-12
}