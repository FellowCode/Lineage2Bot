

#include <Keyboard.h>

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Keyboard.begin();
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0){
    String s = Serial.readString();
    s.trim();
    if (s == "F1"){
      Keyboard.write(KEY_F1);
    } else if (s == "F2"){
      Keyboard.write(KEY_F2);
    } else if (s == "F3"){
      Keyboard.write(KEY_F3);
    } else if (s == "F4"){
      Keyboard.write(KEY_F4);
    } else if (s == "F5"){
      Keyboard.write(KEY_F5);
    } else if (s == "F6"){
      Keyboard.write(KEY_F6);
    } else if (s == "F7"){
      Keyboard.write(KEY_F7);
    } else if (s == "F8"){
      Keyboard.write(KEY_F8);
    } else if (s == "F9"){
      Keyboard.write(KEY_F9);
    } else if (s == "F10"){
      Keyboard.write(KEY_F10);
    } else if (s == "F11"){
      Keyboard.write(KEY_F11);
    } else if (s == "F12"){
      Keyboard.write(KEY_F12);
    } else if (s == "1"){
      Keyboard.write('1');
    } else if (s == "2"){
      Keyboard.write('2');
    } else if (s == "3"){
      Keyboard.write('3');
    } else if (s == "4"){
      Keyboard.write('4');
    } else if (s == "5"){
      Keyboard.write('5');
    } else if (s == "6"){
      Keyboard.write('6');
    } else if (s == "7"){
      Keyboard.write('7');
    } else if (s == "8"){
      Keyboard.write('8');
    } else if (s == "9"){
      Keyboard.write('9');
    } else if (s == "0"){
      Keyboard.write('0');
    }
  }
}
