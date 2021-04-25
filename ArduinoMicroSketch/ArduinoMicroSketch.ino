#include <Keyboard.h>

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0){
    String s = Serial.readString();
    s.trim();
    // Serial.println(s);
    if (s == "F1"){
      Keyboard.write(KEY_F1);
    } else if (s == "F2"){
      Keyboard.write(KEY_F2);
    } else if (s == "1"){
      Keyboard.write('1');
    } else if (s == "2"){
      Keyboard.write('2');
    }
//      case "F1\n": Keyboard.write(KEY_F1); break;
//      case "F2\n": Keyboard.write(KEY_F2); break;
  }
}
