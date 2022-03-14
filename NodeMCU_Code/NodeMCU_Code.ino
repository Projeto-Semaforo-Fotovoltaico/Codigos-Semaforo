#define YellowPin 12
#define RedPin 11
#define GreenPin 10
#define Sensor 9

int varControl;

void setup(){
  pinMode(YellowPin, OUTPUT);
  pinMode(RedPin, OUTPUT);
  pinMode(GreenPin, OUTPUT);
  pinMode(Sensor, INPUT);

  Serial.begin(9600);
}

void loop(){
  digitalWrite(varControl, HIGH);
}
