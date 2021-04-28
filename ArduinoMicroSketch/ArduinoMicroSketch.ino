#include <Keyboard.h>
#include <MouseTo.h>
#include <Mouse.h>

String input = "";
char pressed = '!';

void setup() {
  // put your setup code here, to run once:
  delay(2000);
  Serial.begin(115200);
  Mouse.begin();
}

void processInput(){
  while (Serial.available() > 0){
    char c = Serial.read();
    if (c != ';'){
      input += c;
    } else {
      if (input.indexOf("mouse") >= 0){
        if (input.indexOf("click") >= 0){
          String btn = getValue(input, ' ', 2);
          if (btn == "left")
            Mouse.click(MOUSE_LEFT);
          else if (btn == "right")
            Mouse.click(MOUSE_RIGHT);
          else if (btn == "middle")
            Mouse.click(MOUSE_MIDDLE);            
        } else if (input.indexOf("move") >= 0) {
          String x = getValue(input, ' ', 2);
          String y = getValue(input, ' ', 3);
          mouse_move(x.toInt(), y.toInt());
        }
      } else if (input.indexOf("press") >= 0){
        String key = getValue(input, ' ', 0);
        click_key(key, true);
      } else {
        click_key(input, false);
      }
      input = "";
    }
  }
}

int sign(int val){
  if (val < 0)
    return -1;
  return 1;
}

void mouse_move(int x, int y){
  int moved_x = 0, moved_y = 0;
  while (moved_x != x or moved_y != y){
    int move_x = x-moved_x;
    move_x = min(64, abs(move_x))*sign(move_x);
    int move_y = y-moved_y;
    move_y = min(64, abs(move_y))*sign(move_y);
    Mouse.move(move_x, move_y);
    moved_x += move_x;
    moved_y += move_y;
  }
}

String getValue(String data, char separator, int index)
{
    int found = 0;
    int strIndex[] = { 0, -1 };
    int maxIndex = data.length() - 1;

    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (data.charAt(i) == separator || i == maxIndex) {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    }
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

void click(char key, bool pressKey){
  if (!pressKey || pressed != key)
    release(key);
  Keyboard.press(key);
  delay(10);
  if (!pressKey){
    release(key);
  } else {
    pressed = key;
  }
}

void release(char key){
  Keyboard.release(key);
  delay(10);
}

void click_key(String s, bool pressKey){
    s.trim();
    if (s == "F1"){
      click(KEY_F1, pressKey);
    } else if (s == "F2"){
      click(KEY_F2, pressKey);
    }  else if (s == "F3"){
      click(KEY_F3, pressKey);
    }  else if (s == "F4"){
      click(KEY_F4, pressKey);
    }  else if (s == "F5"){
      click(KEY_F5, pressKey);
    }  else if (s == "F6"){
      click(KEY_F6, pressKey);
    }  else if (s == "F7"){
      click(KEY_F7, pressKey);
    }  else if (s == "F8"){
      click(KEY_F8, pressKey);
    }  else if (s == "F9"){
      click(KEY_F9, pressKey);
    }  else if (s == "F10"){
      click(KEY_F10, pressKey);
    }  else if (s == "F11"){
      click(KEY_F11, pressKey);
    }  else if (s == "F12"){
      click(KEY_F12, pressKey);
    } else if (s == "1"){
      click('1', pressKey);
    } else if (s == "2"){
      click('2', pressKey);
    } else if (s == "3"){
      click('3', pressKey);
    } else if (s == "4"){
      click('4', pressKey);
    } else if (s == "5"){
      click('5', pressKey);
    } else if (s == "6"){
      click('7', pressKey);
    } else if (s == "8"){
      click('8', pressKey);
    } else if (s == "9"){
      click('9', pressKey);
    } else if (s == "0"){
      click('0', pressKey);
    } else if (s == "-"){
      click('-', pressKey);
    } else if (s == "="){
      click('=', pressKey);
    } else if (s == "ESC"){
      click(KEY_ESC, pressKey);
    }
}

void loop() {
  processInput();
}
