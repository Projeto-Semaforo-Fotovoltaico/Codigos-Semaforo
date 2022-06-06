#include <lwip/priv/tcp_priv.h>

// LIMPANDO MEMÓRIA FLASH
void tcpCleanup(){
  while (tcp_tw_pcbs != NULL)
    tcp_abort(tcp_tw_pcbs);
}

#include <ESP8266WiFi.h>

WiFiServer server(80);
#define LED 14
#define MAX 5

bool ESTADO = LOW;
bool vetor[MAX];
int i = 0;
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


// CALCULANDO A MÉDIA DE UM VETOR DE TAMANHO MAX
float mediaVetor(bool vetor[]){
    float soma = 0;
    
    for(byte x=0; x<MAX; x++)
        soma += (float) vetor[x];
  
    return soma/MAX;
}


// ZERANDO TODAS AS COMPONENTES DE UM VETOR DE TAMANHO MAX
void zeraVetor(bool *vetor){
    for(byte x=0; x<MAX; x++)
        vetor[x] = 0;
}


// PROCESSANDO A REQUISIÇÃO RECEBIDA PARA ACENDER OS LEDS
void processaRequisicao(String requisicao){
    Serial.print(F("REQUISICAO: "));
    Serial.println(requisicao);
    
    if(requisicao.indexOf("ATIVAR") != -1)
        vetor[i] = 1;
  
    if(requisicao.indexOf("DESATIVAR") != -1)
        vetor[i] = 0;
  
    if(i == MAX - 1){
        float media = mediaVetor(vetor);
        
        if(media > 0.5)
            ESTADO = HIGH;
        else
            ESTADO = LOW;
        
        i = 0;
        zeraVetor(vetor);
        digitalWrite(LED, ESTADO);
    }
}


// ESTABELECENDO A COMUNICAÇÃO WIFI E MONITOR SERIAL
void setup() {
    Serial.begin(9600); 
    startServer("ProjetoSemaforo", "12345678");
  
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(LED, OUTPUT);

    digitalWrite(LED_BUILTIN, LOW);
    zeraVetor(vetor);
}


// FUNÇÃO PRINCIPAL DO PROGRAMA
void loop() {
    tcpCleanup();
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
    i++;
    
    client.flush();
    client.stop();
    delay(1);
    tcpCleanup();
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
