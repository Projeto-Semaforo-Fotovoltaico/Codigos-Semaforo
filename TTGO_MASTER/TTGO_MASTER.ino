#include <lwip/priv/tcp_priv.h>
#include <WiFi.h>

WiFiServer server(80);
#define LED 0

bool ESTADO = LOW;
void paginaHTML(WiFiClient *cl);


// CRIANDO E INICIANDO O ROTEADOR LOCAL
void startServer(char* nome, char* senha){
    IPAddress staticIP(192, 168, 4, 2);  // IP ESTÁTICO
    IPAddress gateway(192, 168, 4, 1);   // GATEWAY ESTÁTICO IP
    IPAddress subnet(255, 255, 255, 0);  // OCULTAR SUB REDE
  
    // MODO DE TRABALHO WIFI VIA ACESS POINT
    WiFi.mode(WIFI_AP);                 
    WiFi.softAP(nome, senha, 2, 0);
    WiFi.config(staticIP, gateway, subnet);
  
    // INICIALIZANDO O SERVIDOR E IMPRIMINDO INFORMAÇÕES
    server.begin(); 
    Serial.println("SERVER STARTED!"); 
    Serial.println(WiFi.softAPIP());
}


// PROCESSANDO A REQUISIÇÃO RECEBIDA PARA ACENDER OS LEDS
void processaRequisicao(String requisicao){
    Serial.print(F("REQUISICAO: "));
    Serial.println(requisicao);
    
    if(requisicao.indexOf("ATIVAR") != -1)
        ESTADO = HIGH;
  
    if(requisicao.indexOf("DESATIVAR") != -1)
        ESTADO = LOW;

    digitalWrite(LED, ESTADO);
}


// ESTABELECENDO A COMUNICAÇÃO WIFI E MONITOR SERIAL
void setup() {
    Serial.begin(9600); 
    startServer("ProjetoSemaforo", "12345678");
    
    pinMode(LED, OUTPUT);
    digitalWrite(LED, ESTADO);
}


// FUNÇÃO PRINCIPAL DO PROGRAMA
void loop() {
    WiFiClient client = server.available();
  
    // ENQUANTO NÃO FOR CONECTADO NO SERVIDOR CLIENTE
    if (!client)
      return;
  
    // ENQUANTO NÃO FOR RECEBIDA NENHUMA REQUISIÇÃO
    while (!client.available())
      continue;
    
    // LENDO A REQUISIÇÃO RECEBIDA E AUMENTANDO i
    String requisicao = client.readStringUntil('\r');

    if(requisicao.indexOf("/") != -1)
      paginaHTML(&client);
    
    processaRequisicao(requisicao);
    
    client.flush();
    client.stop();
    delay(1);
}


// MONTANDO A PÁGINA HTML PELO ENDEREÇO DE MEMÓRIA DO SERVIDOR CLIENTE
void paginaHTML(WiFiClient *cl){
    (*cl).println("HTTP/1.1 200 OK");
    (*cl).println("Content-Type: text/html");
    (*cl).println("Connection: keep-alive");
    (*cl).println("Keep-Alive: timeout=0.001, max=1000");
    (*cl).println();
    
    (*cl).println("<!DOCTYPE html>");
    (*cl).println("<html>");
   
    (*cl).println("<head>");
    (*cl).println("<title>ESP8266 via WEB</title>");
    (*cl).println("</head>");

    (*cl).println("<body>");
    (*cl).print("<p>GPIO is now ");
    
    if (ESTADO)
        (*cl).println("HIGH</p>");
    else
        (*cl).println("LOW</p>");

    (*cl).println("</body>");
    (*cl).println("</html>");
}
