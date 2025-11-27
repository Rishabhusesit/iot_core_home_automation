/*
 * ESP32 Complete Hardware Integration
 * 
 * Hardware Components:
 * - DHT22: Temperature & Humidity Sensor
 * - PIR Sensor: Motion Detection
 * - Relay Module: Control AC/DC devices
 * - LEDs: Status indicators
 * - Breadboard & Jumper Wires: Connections
 * 
 * Features:
 * - Real-time sensor monitoring
 * - Motion detection with alerts
 * - Relay control via MQTT commands
 * - LED status indicators
 * - AWS IoT Core integration
 * - Bidirectional communication
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include <DHT.h>

// ============================================
// WiFi Configuration
// ============================================
const char* ssid = "Galaxy S23 FE 96CD";
const char* password = "1234567898";

// ============================================
// AWS IoT Core Configuration
// ============================================
const char* aws_iot_endpoint = "aka6dphv0mv57-ats.iot.us-east-1.amazonaws.com";
const int aws_iot_port = 8883;
const char* thing_name = "ESP32_SmartDevice";
const char* client_id = "ESP32_SmartDevice";

// MQTT Topics
const char* topic_publish = "devices/ESP32_SmartDevice/data";
const char* topic_subscribe = "devices/ESP32_SmartDevice/commands";
const char* topic_status = "devices/ESP32_SmartDevice/status";
const char* topic_alerts = "devices/ESP32_SmartDevice/alerts";

// ============================================
// Certificates (Replace with your certificates)
// ============================================
const char* root_ca = \
"-----BEGIN CERTIFICATE-----\n" \
"MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF\n" \
"ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6\n" \
"b24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL\n" \
"MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv\n" \
"b3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj\n" \
"ca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM\n" \
"9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw\n" \
"IFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6\n" \
"VOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L\n" \
"93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm\n" \
"jgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC\n" \
"AYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA\n" \
"A4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI\n" \
"U5PMCCjjmCXPI6T53iHTfIUJrU6adTrCC2qJeHZERxhlbI1Bjjt/msv0tadQ1wUs\n" \
"N+gDS63pYaACbvXy8MWy7Vu33PqUXHeeE6V/Uq2V8viTO96LXFvKWlJbYK8U90vv\n" \
"o/ufQJVtMVT8QtPHRh8jrdkPSHCa2XV4cdFyQzR1bldZwgJcJmApzyMZFo6IQ6XU\n" \
"5MsI+yMRQ+hDKXJioaldXgjUkK642M4UwtBV8ob2xJNDd2ZhwLnoQdeXeGADbkpy\n" \
"rqXRfboQnoZsG4q5WTP468SQvvG5\n" \
"-----END CERTIFICATE-----\n";

const char* device_cert = \
"-----BEGIN CERTIFICATE-----\n" \
"MIIDWTCCAkGgAwIBAgIUT+S99rOpqpU4VlF+P9F3h/sJylowDQYJKoZIhvcNAQEL\n" \
"BQAwTTFLMEkGA1UECwxCQW1hem9uIFdlYiBTZXJ2aWNlcyBPPUFtYXpvbi5jb20g\n" \
"SW5jLiBMPVNlYXR0bGUgU1Q9V2FzaGluZ3RvbiBDPVVTMB4XDTI1MTExNjExMjgx\n" \
"N1oXDTQ5MTIzMTIzNTk1OVowHjEcMBoGA1UEAwwTQVdTIElvVCBDZXJ0aWZpY2F0\n" \
"ZTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALkOP023T7ofYNXJG39R\n" \
"Fg5uZ4nf7tV+E1szSKLioaSWy6cyaUr9PJX7XqR9OFeCHV3LcVc/GJA2vG15QO38\n" \
"aOMDHdSZMYQ30uX0zOz2wZe+gpmwz86nhl1+6RN3G0ZxBD6D7FIlSc/86Z3yEXvk\n" \
"KWO/Y+jUZoJXBIDcKDbQbKrxw8giXSKFTYOw5otGOfS/cIEQHvaJOOdDHaoHqdMY\n" \
"Icw0tDrk/8hEuSCAWH8WsH3gpeUjH9Xx/JUY5f/zAjfWyhJ69wHOVmUOYQ/3XU+a\n" \
"63c+3pD0g/ETrMCaoa76+SocuIKqXun+Bu31suBTldH7wTMwxLlbBbMlOWhQPR9x\n" \
"jDUCAwEAAaNgMF4wHwYDVR0jBBgwFoAUbpDEnczN7X9CzK7eEhZ57djY5AEwHQYD\n" \
"VR0OBBYEFNgkAoxkIjQniGl452mE+F1G6BQyMAwGA1UdEwEB/wQCMAAwDgYDVR0P\n" \
"AQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4IBAQDXg31TG5h/TUaOAuzb6hw4fIto\n" \
"rrTDQTbRoUNoiu/RGLV2+wr5RJo81wSWeToN8vEDUqG/wTWoS2VMz8hO9sFkdLxt\n" \
"zRdtlGuu848BmWjiXqOkZJ4FFeLN5oJqKiPOeM+Az7dyD0LfYudgrTO3KHuaAACf\n" \
"Sk6xgxkP/c0rLSKM6ZGvVBN3YpBbdjO9ABxu2cgM1Qqm39JRyeLqhrSOrAttE7/D\n" \
"veWv7ppmWWuz5Zr5SfdF4PQaL6PLGY7omKh2D+1UwHP0aQ9ey4+r7i4ZmY9p8e3q\n" \
"9RsPeAYOGTNQeGDyuC0olO0Jb7FdFh/W45ijaLM+SqfwZAM3eA10Y/neV1he\n" \
"-----END CERTIFICATE-----\n";

const char* device_key = \
"-----BEGIN RSA PRIVATE KEY-----\n" \
"MIIEowIBAAKCAQEAuQ4/TbdPuh9g1ckbf1EWDm5nid/u1X4TWzNIouKhpJbLpzJp\n" \
"Sv08lftepH04V4IdXctxVz8YkDa8bXlA7fxo4wMd1JkxhDfS5fTM7PbBl76CmbDP\n" \
"zqeGXX7pE3cbRnEEPoPsUiVJz/zpnfIRe+QpY79j6NRmglcEgNwoNtBsqvHDyCJd\n" \
"IoVNg7Dmi0Y59L9wgRAe9ok450Mdqgep0xghzDS0OuT/yES5IIBYfxawfeCl5SMf\n" \
"1fH8lRjl//MCN9bKEnr3Ac5WZQ5hD/ddT5rrdz7ekPSD8ROswJqhrvr5Khy4gqpe\n" \
"6f4G7fWy4FOV0fvBMzDEuVsFsyU5aFA9H3GMNQIDAQABAoIBAH1TiMu5OeVzGsGu\n" \
"UVEIOUfMvZJCdh1gJPu+35Jwqcgt1/6DxYtjtYRdmNsNcvrQw9Kh1UChGqGQcEwz\n" \
"siV6rA4SLkGs/jvtEodqIt7YvoNmIkyz0gjCq9zl9jOYloA+SgGMlp+LYVHaltzA\n" \
"89ZTzzQeiitErafYBtS+RP3aab3al0Yr1t+IsG7/VnAL8LN2jICwMg3OJS3BGSg1\n" \
"kGce2ZGnVqY/U+/pI/GANVogwZ2WA9zD67KstVUzpuWnN0jdQb3LzP7xbJlSTXhp\n" \
"uEyZodMittcbyGTpmwaleBOS+ED38YB6gJIyLHtrmLMebD9qPMuTGylGWH5jwnoX\n" \
"CH42MIECgYEA3I2ARhiC7L+oEcYe7InvMLC40vUqSRn92noMWA94wWJRQXZBrsEF\n" \
"R5oy6BSoOOHNOdf/sxe4EqEbysOEdSB8vkflx5at1rrKz5C3RAQ72oftLyUscSMs\n" \
"4GBDY5KEFdrjCSfKy/LpUH+fTJgU2QmbbY0Kbs1yY68Xeqveisldn9cCgYEA1sw9\n" \
"4o4qJzpA6My1DHOhjZGbHGXGvZ9GsvvZCCOyMun5u8emHl4yl/JAqgjZuj/WsJp5\n" \
"khSmNfw+GQ9QqxVjNqPt5tHxLpORawtj/mcjXdPKtM8obCH2TXt4Scd/fppv16Ka\n" \
"K1j64VuOk+DvvqQSFysiPHi6S5v6LO/6FGfN4tMCgYArdNIOfavmXAkQn3neX3s6\n" \
"m8d/AYF4b9+d2ahu/XVsnSOng1aDyVJx/kcDhXZz5sHaIN4n+odxXD8un4GM1n7d\n" \
"uyriPaU5BwsJBNmnVDI658drH6b3D9g6yZzdlLPj3oIXfritoMop60uG+vw4m3T9\n" \
"i+m/VUmxrIEy0YSC0hRZdwKBgBwmhlHDyfh8JPedpHiuStTv6UEugX5menCImyf6\n" \
"7abIjUcz4iyGseDCCgF+yXIkXbGlfRtNA399wHGuVScm1Wrazxn6F76/7kX2JzO3\n" \
"NqZcVGuf3q9VQB9leB1LPQVNnizHjabysWaJhkURLLpybECHEaSVOe0g0wfCp6a2\n" \
"9/+rAoGBAM4zTz9mtRvsIrr615FCoyHkxXSwJ8KX19s8U6QqM9om0xXtv4SJ6/tZ\n" \
"uCRgLK87KF75nwsCXvB/CUaXdx4TtBy4/qoz70NbJUGvgoHKL/A3BP9D/eLGX+YL\n" \
"0BD1MKaESm9mxXoyA/34fiaS050noqP71zZa9YJ5rHO85fbnE0O/\n" \
"-----END RSA PRIVATE KEY-----\n";

// ============================================
// Hardware Pin Definitions
// ============================================
// DHT22 Temperature & Humidity Sensor
// Wiring: G→GND, OUT→GPIO4, +→3.3V
#define DHT_PIN 4
#define DHT_TYPE DHT22
DHT dht(DHT_PIN, DHT_TYPE);

// PIR Motion Sensor
// Wiring: VCC→VIN, OUT→GPIO13, GND→GND
#define PIR_PIN 13
bool pirState = false;
bool lastPirState = false;
unsigned long lastPirTrigger = 0;
const unsigned long PIR_DEBOUNCE = 2000; // 2 seconds

// Relay Module
// Wiring: VCC→VIN, IN→GPIO12, GND→GND
// Note: If you have a 4-channel relay, you can add more pins below
#define RELAY_1_PIN 12
#define RELAY_2_PIN 19  // Optional: Add more relay pins if needed
#define RELAY_3_PIN 21  // Optional: Add more relay pins if needed
#define RELAY_4_PIN 22  // Optional: Add more relay pins if needed
bool relayStates[4] = {false, false, false, false};

// Status LEDs
#define LED_STATUS_PIN 2      // Built-in LED (WiFi/AWS status)
#define LED_RELAY_1_PIN 25    // Relay 1 status
#define LED_RELAY_2_PIN 26    // Relay 2 status
#define LED_MOTION_PIN 27     // Motion detection indicator

// Button for manual control (optional)
#define BUTTON_PIN 0          // Built-in button

// ============================================
// WiFi and MQTT Clients
// ============================================
WiFiClientSecure net;
PubSubClient client(net);

// ============================================
// Timing Variables
// ============================================
unsigned long lastSensorRead = 0;
unsigned long lastPublish = 0;
const unsigned long SENSOR_READ_INTERVAL = 3000;  // Read sensors every 3 seconds (DHT22 needs 2s between reads)
const unsigned long PUBLISH_INTERVAL = 5000;      // Publish every 5 seconds

// Device state
bool deviceOnline = false;
unsigned long deviceUptime = 0;

// ============================================
// Setup Function
// ============================================
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n========================================");
  Serial.println("ESP32 Complete Hardware Integration");
  Serial.println("========================================\n");
  
  // Note: Watchdog is already initialized by Arduino framework
  // We'll call yield() frequently to prevent timeouts
  
  // Initialize GPIO pins
  setupGPIO();
  
  // Initialize sensors
  // DHT22 needs time to stabilize after power-on
  delay(2000);
  dht.begin();
  delay(1000);  // Additional delay for sensor stabilization
  Serial.println("✅ DHT22 sensor initialized");
  
  // Test DHT22 reading (with yield to prevent watchdog timeout)
  Serial.print("   Testing DHT22... ");
  yield();  // Feed watchdog before sensor read
  delay(100);
  yield();
  float testTemp = dht.readTemperature();
  yield();
  float testHum = dht.readHumidity();
  yield();
  if (!isnan(testTemp) && !isnan(testHum)) {
    Serial.print("OK (T=");
    Serial.print(testTemp);
    Serial.print("°C, H=");
    Serial.print(testHum);
    Serial.println("%)");
  } else {
    Serial.println("⚠️  Warning: Initial read failed (check wiring: G→GND, OUT→GPIO4, +→3.3V)");
  }
  
  // Initialize PIR sensor
  pinMode(PIR_PIN, INPUT);
  Serial.println("✅ PIR sensor initialized");
  
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
  client.setKeepAlive(60);  // Keepalive interval in seconds
  client.setSocketTimeout(15);  // Socket timeout in seconds
  client.setBufferSize(1024);  // Increase buffer size for larger messages
  
  // Connect to AWS IoT
  connectAWS();
  
  // Initial status LED blink
  blinkLED(LED_STATUS_PIN, 3, 200);
  
  Serial.println("\n✅ Setup complete! Starting main loop...\n");
  deviceOnline = true;
}

// ============================================
// Main Loop
// ============================================
void loop() {
  // Feed watchdog timer to prevent timeout
  yield();
  
  // Call client.loop() frequently to maintain connection (non-blocking)
  client.loop();
  
  // Maintain MQTT connection
  if (!client.connected()) {
    deviceOnline = false;
    digitalWrite(LED_STATUS_PIN, LOW);
    connectAWS();
  } else {
    deviceOnline = true;
    digitalWrite(LED_STATUS_PIN, HIGH);
  }
  
  // Update uptime
  deviceUptime = millis() / 1000;
  
  // Read sensors at intervals
  unsigned long currentMillis = millis();
  if (currentMillis - lastSensorRead >= SENSOR_READ_INTERVAL) {
    lastSensorRead = currentMillis;
    readSensors();
    yield();  // Feed watchdog after sensor read
  }
  
  // Publish data at intervals
  if (currentMillis - lastPublish >= PUBLISH_INTERVAL) {
    lastPublish = currentMillis;
    publishSensorData();
    yield();  // Feed watchdog after publish
  }
  
  // Check PIR sensor
  checkPIRSensor();
  
  // Check button (optional manual control)
  checkButton();
  
  // Small delay to prevent tight loop and feed watchdog
  delay(10);
  yield();
}

// ============================================
// GPIO Setup
// ============================================
void setupGPIO() {
  // Relay pins (output)
  pinMode(RELAY_1_PIN, OUTPUT);
  pinMode(RELAY_2_PIN, OUTPUT);
  pinMode(RELAY_3_PIN, OUTPUT);
  pinMode(RELAY_4_PIN, OUTPUT);
  
  // Initialize relays to OFF
  digitalWrite(RELAY_1_PIN, HIGH);  // HIGH = OFF (for active-low relays)
  digitalWrite(RELAY_2_PIN, HIGH);
  digitalWrite(RELAY_3_PIN, HIGH);
  digitalWrite(RELAY_4_PIN, HIGH);
  
  // LED pins (output)
  pinMode(LED_STATUS_PIN, OUTPUT);
  pinMode(LED_RELAY_1_PIN, OUTPUT);
  pinMode(LED_RELAY_2_PIN, OUTPUT);
  pinMode(LED_MOTION_PIN, OUTPUT);
  
  // Button pin (input with pullup)
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  
  Serial.println("✅ GPIO pins initialized");
}

// ============================================
// WiFi Connection
// ============================================
void connectWiFi() {
  Serial.print("📡 Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);  // Disable WiFi sleep to prevent connection issues
  WiFi.setAutoReconnect(true);
  
  // Start connection (non-blocking)
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  unsigned long lastDotTime = 0;
  
  // Non-blocking WiFi connection with very frequent yield() calls
  while (WiFi.status() != WL_CONNECTED && attempts < 120) {
    // Call yield() extremely frequently - every 10ms
    yield();
    delay(10);
    yield();
    delay(10);
    yield();
    delay(10);
    yield();
    delay(10);
    yield();
    delay(10);
    
    // Print progress dot every 500ms
    unsigned long currentTime = millis();
    if (currentTime - lastDotTime >= 500) {
      Serial.print(".");
      blinkLED(LED_STATUS_PIN, 1, 25);
      lastDotTime = currentTime;
    }
    
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi connected!");
    Serial.print("   IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("   Signal strength (RSSI): ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("\n❌ WiFi connection failed!");
    Serial.println("Please check your credentials and try again.");
    while(1) {
      blinkLED(LED_STATUS_PIN, 5, 100);
      delay(1000);
    }
  }
}

// ============================================
// NTP Time Setup
// ============================================
void setupNTP() {
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  
  Serial.print("🕐 Waiting for NTP time sync");
  time_t now = time(nullptr);
  int attempts = 0;
  while (now < 8 * 3600 * 2 && attempts < 20) {
    delay(250);
    yield();  // Feed watchdog during NTP sync
    delay(250);
    yield();
    Serial.print(".");
    now = time(nullptr);
    attempts++;
  }
  
  if (now >= 8 * 3600 * 2) {
    Serial.println("\n✅ NTP time synchronized");
    struct tm timeinfo;
    gmtime_r(&now, &timeinfo);
    Serial.print("   Current time: ");
    Serial.println(asctime(&timeinfo));
  } else {
    Serial.println("\n⚠️  NTP sync failed, continuing anyway");
  }
}

// ============================================
// AWS IoT Connection
// ============================================
void connectAWS() {
  Serial.print("☁️  Connecting to AWS IoT Core...");
  
  int attempts = 0;
  while (!client.connected() && attempts < 5) {
    // Try to connect with clean session
    if (client.connect(client_id, NULL, NULL, 0, 0, 0, 0, 1)) {
      Serial.println("\n✅ Connected to AWS IoT Core!");
      Serial.print("   Client ID: ");
      Serial.println(client_id);
      Serial.print("   Endpoint: ");
      Serial.println(aws_iot_endpoint);
      
      // Subscribe to commands topic
      if (client.subscribe(topic_subscribe, 1)) {
        Serial.print("   ✅ Subscribed to: ");
        Serial.println(topic_subscribe);
      } else {
        Serial.print("   ⚠️  Failed to subscribe to: ");
        Serial.println(topic_subscribe);
      }
      
      // Allow connection to fully establish
      delay(200);
      
      // Call client.loop() to process connection acknowledgment
      client.loop();
      delay(100);
      
      // Publish online status
      publishStatus("online");
      
      return;  // Successfully connected
      
    } else {
      attempts++;
      Serial.print(".");
      Serial.print(" Failed, rc=");
      Serial.print(client.state());
      Serial.print(" (attempt ");
      Serial.print(attempts);
      Serial.println("/5)");
      
      if (attempts < 5) {
        // Break up delay with yield() calls to prevent watchdog timeout
        for (int i = 0; i < 20; i++) {
          delay(100);
          yield();
        }
      } else {
        Serial.println("\n❌ Failed to connect after 5 attempts!");
        Serial.println("   Check your certificates and IoT policy permissions.");
      }
    }
  }
}

// ============================================
// Sensor Reading Functions
// ============================================
void readSensors() {
  // DHT22 readings are handled in publishSensorData()
  // This function can be extended for other sensors
}

void checkPIRSensor() {
  int pirValue = digitalRead(PIR_PIN);
  bool currentPirState = (pirValue == HIGH);
  
  // Detect motion (state change from LOW to HIGH)
  if (currentPirState && !lastPirState) {
    unsigned long currentTime = millis();
    
    // Debounce: only trigger if enough time has passed
    if (currentTime - lastPirTrigger > PIR_DEBOUNCE) {
      pirState = true;
      lastPirTrigger = currentTime;
      
      // Turn on motion LED
      digitalWrite(LED_MOTION_PIN, HIGH);
      
      // Publish motion alert
      publishMotionAlert();
      
      Serial.println("🚨 Motion detected!");
    }
  }
  
  // Turn off motion LED after 2 seconds
  if (pirState && (millis() - lastPirTrigger > 2000)) {
    pirState = false;
    digitalWrite(LED_MOTION_PIN, LOW);
  }
  
  lastPirState = currentPirState;
}

// ============================================
// Relay Control Functions
// ============================================
void controlRelay(int relayNum, bool state) {
  if (relayNum < 1 || relayNum > 4) return;
  
  int relayPin = 0;
  int ledPin = 0;
  
  switch(relayNum) {
    case 1:
      relayPin = RELAY_1_PIN;
      ledPin = LED_RELAY_1_PIN;
      break;
    case 2:
      relayPin = RELAY_2_PIN;
      ledPin = LED_RELAY_2_PIN;
      break;
    case 3:
      relayPin = RELAY_3_PIN;
      break;
    case 4:
      relayPin = RELAY_4_PIN;
      break;
  }
  
  relayStates[relayNum - 1] = state;
  
  // Control relay (HIGH = OFF for active-low relays)
  digitalWrite(relayPin, state ? LOW : HIGH);
  
  // Update status LED
  if (ledPin > 0) {
    digitalWrite(ledPin, state ? HIGH : LOW);
  }
  
  Serial.print("🔌 Relay ");
  Serial.print(relayNum);
  Serial.print(" turned ");
  Serial.println(state ? "ON" : "OFF");
  
  // Publish relay state update
  publishRelayState(relayNum, state);
}

// ============================================
// Button Handler (Optional)
// ============================================
void checkButton() {
  static unsigned long lastButtonPress = 0;
  static bool lastButtonState = HIGH;
  
  bool buttonState = digitalRead(BUTTON_PIN);
  
  // Detect button press (LOW = pressed due to pullup)
  if (buttonState == LOW && lastButtonState == HIGH) {
    unsigned long currentTime = millis();
    
    // Debounce
    if (currentTime - lastButtonPress > 200) {
      lastButtonPress = currentTime;
      
      // Toggle relay 1 as example
      controlRelay(1, !relayStates[0]);
      
      Serial.println("🔘 Button pressed - Toggled Relay 1");
    }
  }
  
  lastButtonState = buttonState;
}

// ============================================
// MQTT Message Callback
// ============================================
void messageCallback(char* topic, byte* payload, unsigned int length) {
  Serial.println("\n========================================");
  Serial.println("📨 Message received!");
  Serial.print("   Topic: ");
  Serial.println(topic);
  Serial.print("   Payload: ");
  
  // Parse JSON payload
  StaticJsonDocument<512> doc;
  deserializeJson(doc, payload, length);
  
  // Print formatted JSON
  serializeJsonPretty(doc, Serial);
  Serial.println();
  
  // Handle commands
  if (doc.containsKey("command")) {
    const char* command = doc["command"];
    Serial.print("   Command: ");
    Serial.println(command);
    
    // Relay control commands
    if (strcmp(command, "relay_control") == 0) {
      if (doc.containsKey("relay") && doc.containsKey("state")) {
        int relayNum = doc["relay"];
        bool state = doc["state"];
        controlRelay(relayNum, state);
      }
    }
    
    // Get status
    else if (strcmp(command, "get_status") == 0) {
      publishStatus("online");
      publishDeviceInfo();
    }
    
    // Reboot device
    else if (strcmp(command, "reboot") == 0) {
      Serial.println("   🔄 Rebooting in 2 seconds...");
      publishStatus("rebooting");
      delay(2000);
      ESP.restart();
    }
    
    // AI response handling
    else if (strcmp(command, "ai_response") == 0 || doc.containsKey("ai_response")) {
      Serial.println("\n   🤖 AI Response received:");
      if (doc.containsKey("ai_response")) {
        const char* aiResponse = doc["ai_response"];
        Serial.println(aiResponse);
        
        // Example: Auto-control relay based on AI recommendation
        if (strstr(aiResponse, "turn on") != NULL || strstr(aiResponse, "activate") != NULL) {
          controlRelay(1, true);
        }
      }
    }
  }
  
  Serial.println("========================================\n");
}

// ============================================
// Publish Functions
// ============================================
void publishSensorData() {
  StaticJsonDocument<512> doc;
  
  // Get timestamp
  time_t now = time(nullptr);
  char timestamp[64];
  struct tm timeinfo;
  gmtime_r(&now, &timeinfo);
  strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
  
  doc["device_id"] = thing_name;
  doc["timestamp"] = timestamp;
  doc["uptime_seconds"] = deviceUptime;
  doc["wifi_rssi"] = WiFi.RSSI();
  doc["free_heap"] = ESP.getFreeHeap();
  
  // Sensor data
  JsonObject sensor_data = doc.createNestedObject("sensor_data");
  
  // DHT22 readings with retry logic
  // DHT22 needs at least 2 seconds between reads
  float temperature = -999;
  float humidity = -999;
  
  // Try reading up to 3 times
  for (int attempt = 0; attempt < 3; attempt++) {
    yield();  // Feed watchdog during retry
    temperature = dht.readTemperature();
    humidity = dht.readHumidity();
    
    if (!isnan(temperature) && !isnan(humidity) && 
        temperature >= -40 && temperature <= 80 && 
        humidity >= 0 && humidity <= 100) {
      // Valid reading
      break;
    } else {
      // Invalid reading, wait before retry
      if (attempt < 2) {
        delay(250);
      }
    }
  }
  
  if (!isnan(temperature) && !isnan(humidity)) {
    sensor_data["temperature"] = temperature;
    sensor_data["humidity"] = humidity;
  } else {
    sensor_data["temperature"] = -999;
    sensor_data["humidity"] = -999;
    Serial.println("⚠️  DHT22 read failed - check wiring (G→GND, OUT→GPIO4, +→3.3V)");
  }
  
  // PIR sensor state
  sensor_data["motion_detected"] = pirState;
  
  // Relay states
  JsonObject relays = doc.createNestedObject("relays");
  relays["relay_1"] = relayStates[0];
  relays["relay_2"] = relayStates[1];
  relays["relay_3"] = relayStates[2];
  relays["relay_4"] = relayStates[3];
  
  // Serialize and publish
  char jsonBuffer[512];
  size_t jsonLength = serializeJson(doc, jsonBuffer);
  
  // Ensure client loop is called to maintain connection
  client.loop();
  
  // Check if client is still connected
  if (!client.connected()) {
    Serial.println("❌ MQTT client not connected! Attempting reconnect...");
    connectAWS();
    return;
  }
  
  // Check client state (0 = MQTT_CONNECTED)
  int clientState = client.state();
  if (clientState != 0) {
    Serial.print("❌ MQTT client state error: ");
    Serial.print(clientState);
    Serial.print(" (0=Connected, -4=Connection timeout, -2=Connection failed)");
    Serial.println(" Attempting reconnect...");
    connectAWS();
    return;
  }
  
  // Publish with QoS 0 (false = QoS 0, true = QoS 1)
  bool publishResult = client.publish(topic_publish, jsonBuffer, false);
  
  if (publishResult) {
    Serial.print("📤 Published sensor data (");
    Serial.print(jsonLength);
    Serial.print(" bytes): ");
    Serial.print("T=");
    Serial.print(temperature);
    Serial.print("°C, H=");
    Serial.print(humidity);
    Serial.print("%, Motion=");
    Serial.println(pirState ? "YES" : "NO");
  } else {
    Serial.print("❌ Publish failed! Client state: ");
    Serial.print(clientState);
    Serial.print(", Connected: ");
    Serial.print(client.connected() ? "YES" : "NO");
    Serial.print(", Payload size: ");
    Serial.print(jsonLength);
    Serial.print(" bytes");
    Serial.print(", Topic: ");
    Serial.println(topic_publish);
    
    // Print the JSON payload for debugging
    Serial.print("Payload: ");
    Serial.println(jsonBuffer);
  }
}

void publishMotionAlert() {
  StaticJsonDocument<256> doc;
  
  time_t now = time(nullptr);
  char timestamp[64];
  struct tm timeinfo;
  gmtime_r(&now, &timeinfo);
  strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
  
  doc["device_id"] = thing_name;
  doc["timestamp"] = timestamp;
  doc["alert_type"] = "motion_detected";
  doc["severity"] = "medium";
  doc["message"] = "Motion detected by PIR sensor";
  
  char jsonBuffer[256];
  serializeJson(doc, jsonBuffer);
  
  client.publish(topic_alerts, jsonBuffer);
  Serial.println("🚨 Published motion alert");
}

void publishStatus(const char* status) {
  if (!client.connected()) {
    Serial.println("⚠️  Cannot publish status - client not connected");
    return;
  }
  
  // Ensure client loop has been called
  client.loop();
  
  StaticJsonDocument<256> doc;
  
  time_t now = time(nullptr);
  char timestamp[64];
  struct tm timeinfo;
  gmtime_r(&now, &timeinfo);
  strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
  
  doc["device_id"] = thing_name;
  doc["timestamp"] = timestamp;
  doc["status"] = status;
  doc["uptime_seconds"] = deviceUptime;
  doc["wifi_rssi"] = WiFi.RSSI();
  doc["free_heap"] = ESP.getFreeHeap();
  
  char jsonBuffer[256];
  size_t jsonLength = serializeJson(doc, jsonBuffer);
  
  bool result = client.publish(topic_status, jsonBuffer, false);
  if (result) {
    Serial.print("📤 Published status: ");
    Serial.println(status);
  } else {
    Serial.print("❌ Failed to publish status. Client state: ");
    Serial.println(client.state());
  }
}

void publishDeviceInfo() {
  StaticJsonDocument<256> doc;
  
  doc["device_id"] = thing_name;
  doc["firmware_version"] = "1.0.0";
  doc["hardware"] = "ESP32";
  doc["sensors"] = "DHT22, PIR";
  doc["actuators"] = "4x Relay, LEDs";
  doc["uptime_seconds"] = deviceUptime;
  doc["free_heap"] = ESP.getFreeHeap();
  
  char jsonBuffer[256];
  serializeJson(doc, jsonBuffer);
  
  String info_topic = String(topic_publish) + "/info";
  client.publish(info_topic.c_str(), jsonBuffer);
}

void publishRelayState(int relayNum, bool state) {
  StaticJsonDocument<256> doc;
  
  time_t now = time(nullptr);
  char timestamp[64];
  struct tm timeinfo;
  gmtime_r(&now, &timeinfo);
  strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
  
  doc["device_id"] = thing_name;
  doc["timestamp"] = timestamp;
  doc["relay"] = relayNum;
  doc["state"] = state;
  
  char jsonBuffer[256];
  serializeJson(doc, jsonBuffer);
  
  String relay_topic = String(topic_publish) + "/relay";
  client.publish(relay_topic.c_str(), jsonBuffer);
}

// ============================================
// Utility Functions
// ============================================
void blinkLED(int pin, int times, int delayMs) {
  for (int i = 0; i < times; i++) {
    digitalWrite(pin, HIGH);
    delay(delayMs);
    digitalWrite(pin, LOW);
    delay(delayMs);
  }
}

