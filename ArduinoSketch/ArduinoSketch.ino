void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  pinMode(A4, OUTPUT); //data flag
  digitalWrite(A4, LOW);
  pinMode(A5, OUTPUT); //pulse
  digitalWrite(A5, LOW);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0){
    int n = Serial.parseInt();
    Serial.println(n);
    digitalWrite(A4, HIGH);
    for (int i=0;i<n;i++){
      digitalWrite(A5, HIGH);
      delay(10);
      digitalWrite(A5, LOW);
      delay(1);
    }
    digitalWrite(A4,LOW);
  }
}
