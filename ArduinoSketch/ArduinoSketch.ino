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
    String s = Serial.readString();
    switch s{
      case "F1": Keyboard.write(KEY_F1); break;
      case "F2": Keyboard.write(KEY_F2); break;
      case "F3": Keyboard.write(KEY_F3); break;
      case "F4": Keyboard.write(KEY_F4); break;
      case "F5": Keyboard.write(KEY_F5); break;
      case "F6": Keyboard.write(KEY_F6); break;
      case "F7": Keyboard.write(KEY_F7); break;
      case "F8": Keyboard.write(KEY_F8); break;
      case "F9": Keyboard.write(KEY_F9); break;
      case "F10": Keyboard.write(KEY_F10); break;
      case "F11": Keyboard.write(KEY_F11); break;
      case "F12": Keyboard.write(KEY_F12); break;
      case "1": Keyboard.write('1'); break;
      case "2": Keyboard.write('2'); break;
      case "3": Keyboard.write('3'); break;
      case "4": Keyboard.write('4'); break;
      case "5": Keyboard.write('5'); break;
      case "6": Keyboard.write('6'); break;
      case "7": Keyboard.write('7'); break;
      case "8": Keyboard.write('8'); break;
      case "9": Keyboard.write('9'); break;
      case "0": Keyboard.write('0'); break;
    }
  }
}
