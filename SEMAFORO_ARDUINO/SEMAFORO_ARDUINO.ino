#define TEMPO_VERDE    10000
#define TEMPO_AMARELO  5000
#define TEMPO_VERMELHO 10000

#define verde     17
#define amarelo   12
#define vermelho  13
#define botao     27

unsigned long contagem = millis();
unsigned long A = millis();
int  x = 0;

void setup(){
    pinMode(verde,    OUTPUT);
    pinMode(amarelo,  OUTPUT);
    pinMode(vermelho, OUTPUT);
  
    pinMode(botao, INPUT_PULLUP);
    Serial.begin(9600);
    
    digitalWrite(verde, HIGH);
    digitalWrite(amarelo,  LOW);
    digitalWrite(vermelho, LOW);

    A = millis();
}


void loop(){
  int estadoBotao = !digitalRead(botao);
  
  if(estadoBotao){
      digitalWrite(verde,    HIGH);
      digitalWrite(vermelho, HIGH);
      digitalWrite(amarelo,  HIGH);
      
      delay(TEMPO_VERMELHO);
    
      x = 0;                // RESET
      contagem = millis();  // RESET
  }
  
  if(x==0){
      digitalWrite(verde,    HIGH);
      digitalWrite(amarelo,  LOW);
      digitalWrite(vermelho, LOW);
  }
  if(x==1){
      digitalWrite(verde,    LOW);
      digitalWrite(amarelo,  HIGH);
      digitalWrite(vermelho, LOW);
  }
  if(x==2){
      digitalWrite(verde,    LOW);
      digitalWrite(amarelo,  LOW);
      digitalWrite(vermelho, HIGH);
  }
  
  bool atualizacao = (x==0 && millis() - contagem > TEMPO_VERDE)   |
                     (x==1 && millis() - contagem > TEMPO_AMARELO) |
                     (x==2 && millis() - contagem > TEMPO_VERMELHO);
                     
  if(atualizacao){
    x++;
    contagem = millis();
    Serial.println(millis()-A);
  }

  if(x == 3)
      x = 0;
}
