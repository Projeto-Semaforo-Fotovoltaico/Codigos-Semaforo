// BIBLIOTECAS UTILIZADAS NESTE CÓDIGO
#include <ESP8266WiFi.h>

#define PINO_DIGITAL   2
#define PINO_ANALOGICO 4
int ESTADO = 1;

// PORTA PADRÃO PARA O SHIELD RECEBER AS REQUISIÇÕES DAS PÁGINAS
WiFiServer server(80);


// TABELA DA VERDADE CRIADA PARA A PASSAGEM DOS PEDESTRES
bool statusPassagem(bool R, bool Y, bool G){
  return R*!Y*!G;
}


// CONECTANDO À REDE LOCAL PELO NOME E SENHA
void conectarRede(char* nomeRede, char* senhaRede){
    WiFi.begin(nomeRede, senhaRede);

    while(WiFi.status() != WL_CONNECTED){
        delay(500);
        Serial.print(".");
    }

    server.begin();
}


// EXIBINDO INFORMAÇÕES DA REDE CONECTADA
void exibirInformacoes(){
    Serial.println("");
    
    if (WiFi.status() == WL_CONNECTED)
        Serial.println("WIFI CONECTADO!");
    else
        Serial.println("WIFI NÃO CONECTADO!");
  
    Serial.print("ENDERECOIP: ");
    Serial.println(WiFi.localIP());
}


// CONFIGURAÇÕES PRINCPAIS NODEMCU
void setup(){
    Serial.begin(9600);
    delay(20);
    
    pinMode(PINO_DIGITAL, OUTPUT);
    digitalWrite(PINO_DIGITAL, 0);

    // CONECTANDO À REDE
    conectarRede("Leonan&Aline", "19021976");
    exibirInformacoes();
}


// FUNÇÃO PARA PISCAR UM LED ESPECIFICADO
void piscaLed(int LED){
    for(int x=0; x<5; x++){
      digitalWrite(LED, HIGH);
      delay(200);
      digitalWrite(LED, LOW);
      delay(200);
    }
}


// FUNÇÃO PRINCIPAL EM LOOP INFINITO
void loop(){
    WiFiClient client = server.available();
    digitalWrite(PINO_DIGITAL, ESTADO);

    // LOOP INFINITO ENQUANTO O SERVIDOR CLIENTE NÃO FOR CONECTADO
    if (!client)
        return;

    // LOOP INFINITO ENQUANTO O SERVIDOR CLIENTE NÃO ESTIVER DISPONÍVEL
    while(!client.available())
      delay(1);
    
    String requisicao = client.readStringUntil('\r');
    Serial.print("REQUISICAO: ");
    Serial.println(requisicao); 

    if(requisicao.indexOf("/gpio/0") != -1){
        ESTADO = 0;
    }
    else if(requisicao.indexOf("/gpio/1") != 1){
        ESTADO = 1;
    }
    else{
        Serial.println("requisicao invalida!");
        client.stop();
        return;
    }

    
    client.flush();
    
    client.println("HTPP/1.1 200 OK"); 
    client.println("Content-Type: text/html");
    client.println("Connection: keep-alive");
    client.println();
    
    client.println("<!DOCTYPE HTML>");
    client.println("<html>");

    client.println("<head>");
    client.print("<title>GPIO is now ");
    
    if (ESTADO)
        client.print("HIGH");
    else
        client.print("LOW");

    client.println("</title>");
    client.println("</head>");
    client.println("</html>");
    
    delay(1);
}
