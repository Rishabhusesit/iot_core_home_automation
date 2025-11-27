/*
 * PIR Motion Sensor Test (HC-SR501)
 * 
 * Connections:
 * - VCC → 5V (or 3.3V if module supports)
 * - OUT → GPIO 5
 * - GND → GND
 */

#define PIR_PIN 5

void setup() {
  Serial.begin(115200);
  Serial.println("PIR Motion Sensor Test Starting...");
  pinMode(PIR_PIN, INPUT);
  delay(30000); // Wait for PIR to stabilize (30 seconds)
  Serial.println("✅ PIR sensor ready!");
  Serial.println("Wave your hand in front of the sensor...");
}

void loop() {
  int motion = digitalRead(PIR_PIN);
  
  if (motion == HIGH) {
    Serial.println("🔴 MOTION DETECTED!");
  } else {
    Serial.println("⚪ No motion");
  }
  
  delay(500); // Check every 500ms
}
