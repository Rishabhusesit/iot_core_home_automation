/*
 * DHT22 Temperature & Humidity Sensor Test
 * 
 * Connections:
 * - VCC  → 3.3V
 * - DATA → GPIO 4
 * - GND  → GND
 * - 10kΩ resistor between DATA and VCC
 */

#include <DHT.h>

#define DHTPIN 4
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  Serial.println("DHT22 Test Starting...");
  dht.begin();
  delay(2000); // Wait for sensor to stabilize
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("❌ Failed to read from DHT22!");
    Serial.println("Check wiring:");
    Serial.println("  - VCC to 3.3V");
    Serial.println("  - DATA to GPIO 4");
    Serial.println("  - GND to GND");
    Serial.println("  - 10kΩ resistor between DATA and VCC");
  } else {
    Serial.print("✅ Temperature: ");
    Serial.print(temperature);
    Serial.print("°C | Humidity: ");
    Serial.print(humidity);
    Serial.println("%");
  }
  
  delay(2000); // Wait 2 seconds between readings
}
