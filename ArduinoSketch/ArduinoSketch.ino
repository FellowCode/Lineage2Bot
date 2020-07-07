#define FLAG_PIN 9
#define PULSE_PIN 5

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  pinMode(FLAG_PIN, OUTPUT); //data flag
  digitalWrite(FLAG_PIN, LOW);
  pinMode(PULSE_PIN, OUTPUT); //pulse
  digitalWrite(PULSE_PIN, LOW);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0){
    int n = Serial.parseInt();
    Serial.println(n);
    digitalWrite(FLAG_PIN, HIGH);
    for (int i=0;i<n;i++){
      digitalWrite(PULSE_PIN, HIGH);
      delay(1);
      digitalWrite(PULSE_PIN, LOW);
      delay(1);
    }
    digitalWrite(FLAG_PIN,LOW);
  }
}
