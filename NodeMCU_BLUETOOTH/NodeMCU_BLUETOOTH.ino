#include <SoftwareSerial.h>
SoftwareSerial btSerial(D2, D3);

void setup(){
  pinMode(D5, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  btSerial.begin(9600);
  Serial.println("Começado...");
}

void loop(){
   if (btSerial.available()) {
    String data = btSerial.readString();
    Serial.println(data);
    
    if (data.indexOf("LIGA")){
      digitalWrite(D5, HIGH);
      digitalWrite(LED_BUILTIN, HIGH);
    }if (data.indexOf("DESLIGA")){
      digitalWrite(D5, LOW);
      digitalWrite(LED_BUILTIN, LOW);
    }
    delay(500);
  }
}
