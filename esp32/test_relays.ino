/*
 * 4-Channel Relay Module Test
 * 
 * Connections:
 * - VCC → 5V
 * - IN1 → GPIO 18
 * - IN2 → GPIO 19
 * - IN3 → GPIO 21
 * - IN4 → GPIO 22
 * - GND → GND
 * 
 * Note: Most relay modules are active-LOW (LOW = ON, HIGH = OFF)
 */

#define RELAY1 18
#define RELAY2 19
#define RELAY3 21
#define RELAY4 22

void setup() {
  Serial.begin(115200);
  Serial.println("Relay Module Test Starting...");
  
  pinMode(RELAY1, OUTPUT);
  pinMode(RELAY2, OUTPUT);
  pinMode(RELAY3, OUTPUT);
  pinMode(RELAY4, OUTPUT);
  
  // Initialize all relays to OFF (HIGH for active-low)
  digitalWrite(RELAY1, HIGH);
  digitalWrite(RELAY2, HIGH);
  digitalWrite(RELAY3, HIGH);
  digitalWrite(RELAY4, HIGH);
  
  Serial.println("✅ All relays initialized to OFF");
  delay(1000);
}

void loop() {
  // Test Relay 1
  Serial.println("Testing Relay 1...");
  digitalWrite(RELAY1, LOW);  // Turn ON
  Serial.println("  Relay 1: ON (should hear click)");
  delay(2000);
  digitalWrite(RELAY1, HIGH); // Turn OFF
  Serial.println("  Relay 1: OFF");
  delay(1000);
  
  // Test Relay 2
  Serial.println("Testing Relay 2...");
  digitalWrite(RELAY2, LOW);
  Serial.println("  Relay 2: ON");
  delay(2000);
  digitalWrite(RELAY2, HIGH);
  Serial.println("  Relay 2: OFF");
  delay(1000);
  
  // Test Relay 3
  Serial.println("Testing Relay 3...");
  digitalWrite(RELAY3, LOW);
  Serial.println("  Relay 3: ON");
  delay(2000);
  digitalWrite(RELAY3, HIGH);
  Serial.println("  Relay 3: OFF");
  delay(1000);
  
  // Test Relay 4
  Serial.println("Testing Relay 4...");
  digitalWrite(RELAY4, LOW);
  Serial.println("  Relay 4: ON");
  delay(2000);
  digitalWrite(RELAY4, HIGH);
  Serial.println("  Relay 4: OFF");
  delay(1000);
  
  Serial.println("\n--- Cycle complete, repeating... ---\n");
}
