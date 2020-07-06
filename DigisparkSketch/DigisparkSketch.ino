#include <DigiKeyboard.h>

byte rcv;
boolean readData = false;
boolean pulse = false;

void setup() {
  pinMode(0, INPUT); //flag
  pinMode(2, INPUT); //pulse
  pinMode(1, OUTPUT); //led
  digitalWrite(1, HIGH);
  delay(1000);
  digitalWrite(1, LOW);
}

void loop() {
  digitalWrite(1, digitalRead(2));
  if (digitalRead(0) == 1){
    if (!readData){
      readData = true;
      rcv = 0;
    }
    if (!pulse && digitalRead(2) == 1){
      rcv++;
      pulse = true;
    }
    if (digitalRead(2) == 0){
      pulse = false;
    }
  } else {
    if (readData){
      onReceive(rcv);
    }
    readData = false;
  }
}

void onReceive(byte data){
  switch (data){
    case 1: DigiKeyboard.sendKeyStroke(KEY_F1); break;
    case 2: DigiKeyboard.sendKeyStroke(KEY_F2); break;
    case 3: DigiKeyboard.sendKeyStroke(KEY_F3); break;
    case 4: DigiKeyboard.sendKeyStroke(KEY_F4); break;
    case 5: DigiKeyboard.sendKeyStroke(KEY_F5); break;
    case 6: DigiKeyboard.sendKeyStroke(KEY_F6); break;
    case 7: DigiKeyboard.sendKeyStroke(KEY_F7); break;
    case 8: DigiKeyboard.sendKeyStroke(KEY_F8); break;
    case 9: DigiKeyboard.sendKeyStroke(KEY_F9); break;
    case 10: DigiKeyboard.sendKeyStroke(KEY_F10); break;
    case 11: DigiKeyboard.sendKeyStroke(KEY_F11); break;
    case 12: DigiKeyboard.sendKeyStroke(KEY_F12); break;
    case 13: DigiKeyboard.sendKeyStroke(KEY_1); break;
    case 14: DigiKeyboard.sendKeyStroke(KEY_2); break;
    case 15: DigiKeyboard.sendKeyStroke(KEY_3); break;
    case 16: DigiKeyboard.sendKeyStroke(KEY_4); break;
    case 17: DigiKeyboard.sendKeyStroke(KEY_5); break;
    case 18: DigiKeyboard.sendKeyStroke(KEY_6); break;
    case 19: DigiKeyboard.sendKeyStroke(KEY_7); break;
  }
}
