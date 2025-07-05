#include <Wire.h>                    // Library for I2C communication
#include <LiquidCrystal_I2cTUR.h>    // Library for I2C LCD with TUR extension

// Initialize the LCD object at I2C address 0x27, with 16 characters and 2 lines
LiquidCrystal_I2cTUR lcd(0x27, 16, 2);

#define enablePin       25          // PWM pin to enable/disable motor driver
#define directionPin1   26          // Motor direction control pin 1
#define directionPin2   27          // Motor direction control pin 2

#define buzzer          14          // Pin connected to buzzer

#define proximityTrig   13          // HC-SR04 trigger pin for proximity sensor
#define proximityEcho   32          // HC-SR04 echo pin for proximity sensor

#define SDA_PIN         21          // I2C data pin (ESP32)
#define SCL_PIN         22          // I2C clock pin (ESP32)

#define MAX_VALUE       400         // Maximum valid distance value (cm)
#define MIN_VALUE       2           // Minimum valid distance value (cm)

float distance = 0;                  // Measured distance (in cm)
bool direction = true;               // Current motor direction: true = forward, false = reverse
int measureCounter = 0;              // Counter for number of measurements taken
int measuredDistances[90];           // Optional array to store up to 90 distance readings (not used here)

// Toggles motor direction by switching directionPin1/2 outputs
void changeDirection() {
  if (direction) {
    // Currently moving forward; switch to reverse
    digitalWrite(directionPin1, LOW);
    digitalWrite(directionPin2, HIGH);
    direction = false;
  } else {
    // Currently moving reverse; switch to forward
    digitalWrite(directionPin1, HIGH);
    digitalWrite(directionPin2, LOW);
    direction = true;
  }
}

// Starts or stops the motor: if isTrue==true, both direction pins are LOW (motor stopped)
// If isTrue==false, motor runs in the last known 'direction'
void startStop(bool isTrue) {
  if (isTrue) {
    // Stop motor by disabling both direction pins
    digitalWrite(directionPin1, LOW);
    digitalWrite(directionPin2, LOW);
  } else {
    // Resume motor movement in the current 'direction'
    if (!direction) {
      // Reverse direction
      digitalWrite(directionPin1, LOW);
      digitalWrite(directionPin2, HIGH);
    } else {
      // Forward direction
      digitalWrite(directionPin1, HIGH);
      digitalWrite(directionPin2, LOW);
    }
  }
}

// Sends a 10µs HIGH pulse to the HC-SR04 trigger pin to initiate a distance measurement
void triggerSensor() {
  digitalWrite(proximityTrig, LOW);
  delayMicroseconds(2);
  digitalWrite(proximityTrig, HIGH);
  delayMicroseconds(10);
  digitalWrite(proximityTrig, LOW);
}

// Measures the duration of the HIGH pulse on the HC-SR04 echo pin (in microseconds)
long measureEchoDuration() {
  return pulseIn(proximityEcho, HIGH);
}

// Calculates distance in centimeters based on echo duration
float calculateDistanceCM() {
  triggerSensor();                             // Send trigger pulse
  long duration = measureEchoDuration();       // Read echo pulse duration
  float distance = duration * 0.034 / 2;       // Convert duration to distance (sound speed ~343 m/s)
  // If measured distance is within the sensor's valid range, return it; otherwise return 0
  if (distance >= MIN_VALUE && distance <= MAX_VALUE) {
    return distance;
  }
  return 0;
}

void setup() {
  // Initialize I2C communication (for the LCD)
  Wire.begin();
  lcd.init();                    // Initialize the I2C LCD
  lcd.backlight();               // Turn on the LCD backlight

  // Serial port for debugging and communication with Python on PC
  Serial.begin(115200);

  // Configure motor control pins as outputs
  pinMode(directionPin1, OUTPUT);
  pinMode(directionPin2, OUTPUT);
  pinMode(enablePin, OUTPUT);

  // Configure buzzer pin as output
  pinMode(buzzer, OUTPUT);

  // Configure proximity sensor pins: trigger as output, echo as input
  pinMode(proximityTrig, OUTPUT);
  pinMode(proximityEcho, INPUT);

  // Enable motor driver at full speed (255 = 100% duty cycle)
  analogWrite(enablePin, 255);

  // Display startup message on LCD
  lcd.setCursor(0, 0);
  lcd.print("Python beklenior");  // "Waiting for Python" in Turkish

  // Wait until the PC-side Python script sends an "RDY" message
  while (true) {
    Serial.println("ESP32: Waiting for RDY signal...");
    if (Serial.available()) {
      String input = Serial.readStringUntil('\n');
      if (input == "RDY\r") {
        // Ready signal received: stop the motor and break out of loop
        Serial.println("ESP32: Ready signal received.");
        startStop(false);         // Ensure motor runs in default direction after ready
        break;
      }
    }
    delay(100);
  }

  // Clear the LCD after initialization is complete
  lcd.clear();
}

void loop() {
  // Small delay before each cycle to avoid flooding serial prints
  delay(70);

  // Stop motor briefly to take a stable measurement
  startStop(true);

  // Inform PC-side script that we're about to measure
  Serial.printf("FWR\n\r");   // Custom code: "FWR" could signal "forward measurement request"

  // Measure distance and display on LCD
  distance = calculateDistanceCM();
  lcd.setCursor(0, 0);
  lcd.print("Distance:");     // Label
  lcd.setCursor(10, 0);
  lcd.print(distance);        // Numeric value in cm
  delay(60);                  // Brief pause to allow LCD to update
  Serial.printf("Distance: %f\n\r", distance);  // Send distance over serial for logging

  // After 90 measurements, change the motor direction
  if (measureCounter > 89) {
    measureCounter = 0;
    Serial.printf("CDR\n\r");  // Custom code: "CDR" could signal "change direction"
    changeDirection();
  }

  // Resume motor movement
  startStop(false);

  // Increment the measurement counter
  measureCounter++;
}
