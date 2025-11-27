/*
 * ESP32 AWS IoT Core Integration
 * 
 * This sketch connects an ESP32 to AWS IoT Core using MQTT
 * Publishes sensor data and subscribes to commands
 * 
 * Hardware Requirements:
 * - ESP32 Development Board
 * - Optional: DHT22 temperature/humidity sensor
 * - Optional: BMP280 pressure sensor
 * 
 * Libraries Required:
 * - WiFi (built-in)
 * - WiFiClientSecure (built-in)
 * - PubSubClient by Nick O'Leary
 * - ArduinoJson by Benoit Blanchon
 * - DHT sensor library (if using DHT22)
 * - Adafruit BMP280 (if using BMP280)
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <time.h>

// WiFi Credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// AWS IoT Core Configuration
const char* aws_iot_endpoint = "YOUR_ENDPOINT.iot.REGION.amazonaws.com";
const int aws_iot_port = 8883;
const char* thing_name = "ESP32_Device";
const char* client_id = "ESP32_Device";

// MQTT Topics
const char* topic_publish = "devices/ESP32_Device/data";
const char* topic_subscribe = "devices/ESP32_Device/commands";

// Certificate and Key (will be stored in PROGMEM)
// Replace with your actual certificates from AWS IoT
const char* root_ca = \
"-----BEGIN CERTIFICATE-----\n" \
"YOUR_ROOT_CA_CERTIFICATE_HERE\n" \
"-----END CERTIFICATE-----\n";

const char* device_cert = \
"-----BEGIN CERTIFICATE-----\n" \
"YOUR_DEVICE_CERTIFICATE_HERE\n" \
"-----END CERTIFICATE-----\n";

const char* device_key = \
"-----BEGIN RSA PRIVATE KEY-----\n" \
"YOUR_PRIVATE_KEY_HERE\n" \
"-----END RSA PRIVATE KEY-----\n";

// WiFi and MQTT Clients
WiFiClientSecure net;
PubSubClient client(net);

// Timing
unsigned long lastMillis = 0;
const unsigned long publishInterval = 5000; // 5 seconds

// Sensor pins (adjust based on your hardware)
#ifdef USE_DHT22
#include <DHT.h>
#define DHT_PIN 4
#define DHT_TYPE DHT22
DHT dht(DHT_PIN, DHT_TYPE);
#endif

#ifdef USE_BMP280
#include <Adafruit_BMP280.h>
Adafruit_BMP280 bmp;
#endif

// Function prototypes
void connectWiFi();
void connectAWS();
void messageCallback(char* topic, byte* payload, unsigned int length);
void publishSensorData();
void setupNTP();

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n========================================");
  Serial.println("ESP32 AWS IoT Core Integration");
  Serial.println("========================================\n");
  
  // Initialize sensors
  #ifdef USE_DHT22
    dht.begin();
    Serial.println("DHT22 sensor initialized");
  #endif
  
  #ifdef USE_BMP280
    if (!bmp.begin(0x76)) {
      Serial.println("BMP280 sensor not found!");
    } else {
      Serial.println("BMP280 sensor initialized");
    }
  #endif
  
  // Connect to WiFi
  connectWiFi();
  
  // Setup NTP for accurate timestamps
  setupNTP();
  
  // Configure MQTT client
  net.setCACert(root_ca);
  net.setCertificate(device_cert);
  net.setPrivateKey(device_key);
  
  client.setServer(aws_iot_endpoint, aws_iot_port);
  client.setCallback(messageCallback);
  
  // Connect to AWS IoT
  connectAWS();
  
  Serial.println("\nSetup complete! Starting main loop...\n");
}

void loop() {
  // Maintain MQTT connection
  if (!client.connected()) {
    connectAWS();
  }
  client.loop();
  
  // Publish sensor data at intervals
  unsigned long currentMillis = millis();
  if (currentMillis - lastMillis >= publishInterval) {
    lastMillis = currentMillis;
    publishSensorData();
  }
  
  delay(100);
}

void connectWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal strength (RSSI): ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("\nWiFi connection failed!");
    Serial.println("Please check your credentials and try again.");
    while(1) delay(1000); // Halt
  }
}

void setupNTP() {
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  
  Serial.print("Waiting for NTP time sync");
  time_t now = time(nullptr);
  int attempts = 0;
  while (now < 8 * 3600 * 2 && attempts < 20) {
    delay(500);
    Serial.print(".");
    now = time(nullptr);
    attempts++;
  }
  
  if (now >= 8 * 3600 * 2) {
    Serial.println("\nNTP time synchronized");
    struct tm timeinfo;
    gmtime_r(&now, &timeinfo);
    Serial.print("Current time: ");
    Serial.println(asctime(&timeinfo));
  } else {
    Serial.println("\nNTP sync failed, continuing anyway");
  }
}

void connectAWS() {
  Serial.print("Connecting to AWS IoT Core...");
  
  while (!client.connected()) {
    if (client.connect(client_id)) {
      Serial.println("\nConnected to AWS IoT Core!");
      
      // Subscribe to commands topic
      if (client.subscribe(topic_subscribe)) {
        Serial.print("Subscribed to: ");
        Serial.println(topic_subscribe);
      } else {
        Serial.println("Failed to subscribe!");
      }
    } else {
      Serial.print(".");
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}

void messageCallback(char* topic, byte* payload, unsigned int length) {
  Serial.println("\n========================================");
  Serial.println("Message received!");
  Serial.print("Topic: ");
  Serial.println(topic);
  Serial.print("Payload: ");
  
  // Parse JSON payload
  StaticJsonDocument<256> doc;
  deserializeJson(doc, payload, length);
  
  // Print formatted JSON
  serializeJsonPretty(doc, Serial);
  Serial.println();
  
  // Handle commands
  if (doc.containsKey("command")) {
    const char* command = doc["command"];
    Serial.print("Command: ");
    Serial.println(command);
    
    // Example command handling
    if (strcmp(command, "get_status") == 0) {
      publishStatus();
    } else if (strcmp(command, "set_interval") == 0) {
      if (doc.containsKey("interval")) {
        // Update publish interval (in milliseconds)
        // Note: This would require a global variable
        Serial.print("Setting interval to: ");
        Serial.println(doc["interval"].as<int>());
      }
    } else if (strcmp(command, "reboot") == 0) {
      Serial.println("Rebooting in 2 seconds...");
      delay(2000);
      ESP.restart();
    }
  }
  
  // Handle AI responses from Bedrock
  if (doc.containsKey("ai_response")) {
    Serial.println("\n🤖 AI Response received:");
    Serial.println(doc["ai_response"].as<const char*>());
    
    // You can add logic here to act on AI responses
    // For example, control actuators, LEDs, etc.
  }
  
  Serial.println("========================================\n");
}

void publishSensorData() {
  // Create JSON document
  StaticJsonDocument<512> doc;
  
  // Get timestamp
  time_t now = time(nullptr);
  char timestamp[64];
  struct tm timeinfo;
  gmtime_r(&now, &timeinfo);
  strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
  
  doc["device_id"] = thing_name;
  doc["timestamp"] = timestamp;
  doc["wifi_rssi"] = WiFi.RSSI();
  
  // Read sensor data
  JsonObject sensor_data = doc.createNestedObject("sensor_data");
  
  #ifdef USE_DHT22
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    
    if (!isnan(temperature) && !isnan(humidity)) {
      sensor_data["temperature"] = temperature;
      sensor_data["humidity"] = humidity;
    } else {
      Serial.println("Failed to read DHT22 sensor!");
    }
  #endif
  
  #ifdef USE_BMP280
    float pressure = bmp.readPressure() / 100.0; // Convert to hPa
    float altitude = bmp.readAltitude(1013.25); // Sea level pressure
    
    if (!isnan(pressure)) {
      sensor_data["pressure"] = pressure;
      sensor_data["altitude"] = altitude;
    }
  #endif
  
  // If no sensors, use simulated data
  #if !defined(USE_DHT22) && !defined(USE_BMP280)
    sensor_data["temperature"] = 25.0 + (random(0, 100) / 10.0);
    sensor_data["humidity"] = 50.0 + (random(0, 100) / 10.0);
    sensor_data["pressure"] = 1013.25;
  #endif
  
  // Serialize and publish
  char jsonBuffer[512];
  serializeJson(doc, jsonBuffer);
  
  if (client.publish(topic_publish, jsonBuffer)) {
    Serial.print("📤 Published: ");
    Serial.println(jsonBuffer);
  } else {
    Serial.println("❌ Publish failed!");
  }
}

void publishStatus() {
  StaticJsonDocument<256> doc;
  
  time_t now = time(nullptr);
  char timestamp[64];
  struct tm timeinfo;
  gmtime_r(&now, &timeinfo);
  strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
  
  doc["device_id"] = thing_name;
  doc["timestamp"] = timestamp;
  doc["status"] = "online";
  doc["uptime_seconds"] = millis() / 1000;
  doc["free_heap"] = ESP.getFreeHeap();
  doc["wifi_rssi"] = WiFi.RSSI();
  
  char jsonBuffer[256];
  serializeJson(doc, jsonBuffer);
  
  String status_topic = String(topic_publish) + "/status";
  client.publish(status_topic.c_str(), jsonBuffer);
  
  Serial.print("📤 Published status: ");
  Serial.println(jsonBuffer);
}







