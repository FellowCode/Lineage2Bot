#include <DigiKeyboard.h>

byte rcv;
boolean readData = false;
boolean pulse = false;

void setup() {
  pinMode(0, INPUT); //flag
  pinMode(2, INPUT); //pulse
  pinMode(1, OUTPUT); //led
  digitalWrite(1, LOW);
}

void loop() {
  digitalWrite(1, digitalRead(0));
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
  DigiKeyboard.print("Get"+String(data));
  switch (data){
    case 49: DigiKeyboard.sendKeyStroke(KEY_1); break;
    case 50: DigiKeyboard.sendKeyStroke(KEY_2); break;
    case 51: DigiKeyboard.sendKeyStroke(KEY_3); break;
    case 52: DigiKeyboard.sendKeyStroke(KEY_F4); break;
    case 53: DigiKeyboard.sendKeyStroke(KEY_F5); break;
    case 54: DigiKeyboard.sendKeyStroke(KEY_F6); break;
    case 55: DigiKeyboard.sendKeyStroke(KEY_F7); break;
    case 56: DigiKeyboard.sendKeyStroke(KEY_F8); break;
    case 57: DigiKeyboard.sendKeyStroke(KEY_F9); break;
    case 58: DigiKeyboard.sendKeyStroke(KEY_F10); break;
    case 59: DigiKeyboard.sendKeyStroke(KEY_F11); break;
    case 60: DigiKeyboard.sendKeyStroke(KEY_F12); break;
  }
}
