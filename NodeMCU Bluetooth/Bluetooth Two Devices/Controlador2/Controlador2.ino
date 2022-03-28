#include <SoftwareSerial.h>

SoftwareSerial bluetooth(D2, D3);
String texto;
char data;

void setup(){
  pinMode(D5, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  
  Serial.begin(9600);
  bluetooth.begin(9600);
  
  Serial.println("Começado...");
}

void loop(){
   // SE CHEGOU ALGUM DADO PARA SER LIDO VIA BLUETOOTH (RECEBER DADOS)
   if (bluetooth.available()){
      texto = bluetooth.readString();
      Serial.println(texto);
      
      if (texto.indexOf("LIGA")){
          digitalWrite(D5, HIGH);
          digitalWrite(LED_BUILTIN, HIGH);
      }
      if (texto.indexOf("DESLIGA")){
          digitalWrite(D5, LOW);
          digitalWrite(LED_BUILTIN, LOW);
      }
      delay(500);
  }

  // SE EXISTEM CARACTERES DIGITADOS NO SERIAL MONITOR (ENVIAR DADOS)
  if (Serial.available()){
      data = Serial.read();
      bluetooth.write(data);
   }
}
