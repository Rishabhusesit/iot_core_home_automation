/*
 * LED Test
 * 
 * Connections:
 * - LED 1: GPIO 25 → 220Ω resistor → GND
 * - LED 2: GPIO 26 → 220Ω resistor → GND
 * - LED 3: GPIO 27 → 220Ω resistor → GND
 * 
 * Note: Long leg (anode) goes to GPIO, short leg (cathode) to GND
 */

#define LED1 25
#define LED2 26
#define LED3 27

void setup() {
  Serial.begin(115200);
  Serial.println("LED Test Starting...");
  
  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(LED3, OUTPUT);
  
  // Turn all LEDs off initially
  digitalWrite(LED1, LOW);
  digitalWrite(LED2, LOW);
  digitalWrite(LED3, LOW);
  
  Serial.println("✅ LEDs initialized");
  delay(1000);
}

void loop() {
  // Test LED 1
  Serial.println("LED 1 ON");
  digitalWrite(LED1, HIGH);
  delay(500);
  digitalWrite(LED1, LOW);
  delay(200);
  
  // Test LED 2
  Serial.println("LED 2 ON");
  digitalWrite(LED2, HIGH);
  delay(500);
  digitalWrite(LED2, LOW);
  delay(200);
  
  // Test LED 3
  Serial.println("LED 3 ON");
  digitalWrite(LED3, HIGH);
  delay(500);
  digitalWrite(LED3, LOW);
  delay(200);
  
  // All LEDs on
  Serial.println("All LEDs ON");
  digitalWrite(LED1, HIGH);
  digitalWrite(LED2, HIGH);
  digitalWrite(LED3, HIGH);
  delay(1000);
  
  // All LEDs off
  Serial.println("All LEDs OFF");
  digitalWrite(LED1, LOW);
  digitalWrite(LED2, LOW);
  digitalWrite(LED3, LOW);
  delay(1000);
  
  Serial.println("--- Cycle complete ---\n");
}
