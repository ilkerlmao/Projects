// Solar Panel Data Logger 
// Compatible with Serial Plotter & CoolTerm

const int panel1Pin = A0; 
const int panel2Pin = A1; 

void setup() {
  Serial.begin(9600);
  // We do NOT print headers here (like "Volts") 
  // because text ruins the Serial Plotter graph.
}

void loop() {
  // Read the analog pins
  int rawValue1 = analogRead(panel1Pin);
  int rawValue2 = analogRead(panel2Pin);
  
  // Convert to voltage (assuming a 5V board)
  float voltage1 = rawValue1 * (5.0 / 1023.0);
  float voltage2 = rawValue2 * (5.0 / 1023.0);
  
  // Send data formatted for both Plotter and CSV
  Serial.print(voltage1);
  Serial.print(",");         // Comma delimiter for Excel/Plotter
  Serial.println(voltage2);  // println moves to the next line
  
  delay(250); // Takes a reading every half-second. Change this to 1000 for 1 sec.
}