#define VERMELHO 12
#define AMARELO  11
#define VERDE    10

void setup() {
  pinMode(VERMELHO, OUTPUT);
  pinMode(AMARELO,  OUTPUT);
  pinMode(VERDE,    OUTPUT);
}

void loop(){
  digitalWrite(VERMELHO, LOW);
  digitalWrite(AMARELO,  LOW);
  digitalWrite(VERDE,    HIGH);
  delay(5000);

  digitalWrite(VERMELHO, LOW);
  digitalWrite(AMARELO,  HIGH);
  digitalWrite(VERDE,    LOW);
  delay(2000);
  
  digitalWrite(VERMELHO, HIGH);
  digitalWrite(AMARELO,  LOW);
  digitalWrite(VERDE,    LOW);
  delay(5000);
}
