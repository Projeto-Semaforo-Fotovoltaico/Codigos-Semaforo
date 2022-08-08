#include <lwip/priv/tcp_priv.h>

// LIMPANDO MEMÓRIA FLASH
void tcpCleanup(){
  while (tcp_tw_pcbs != NULL)
    tcp_abort(tcp_tw_pcbs);
}

#include <ESP8266WiFi.h>

WiFiServer server(80);
#define LED 14

bool ESTADO = LOW;
void paginaHTML(WiFiClient *cl);


// CONECTANDO À REDE LOCAL PELO NOME E SENHA
void conectarRede(char* nomeRede, char* senhaRede){
    WiFi.mode(WIFI_STA);
    WiFi.begin(nomeRede, senhaRede);

    // (OPCIONAL) CONFIGURAÇÕES SECUNDÁRIAS DO SERVIDOR LOCAL
    IPAddress staticIP(192, 168, 4, 3);     // IP ESTÁTICO (USADO PARA AS REQUISIÇÕES)
    IPAddress gateway(192, 168, 4, 2);      // GATEWAY ESTÁTICO IP
    IPAddress subnet(255, 255, 255, 0);     // OCULTAR SUB REDE
    WiFi.config(staticIP, gateway, subnet);

    while(WiFi.status() != WL_CONNECTED){
        delay(500);
        Serial.print(F("."));
    }

    server.begin();
}


// EXIBINDO INFORMAÇÕES DA REDE CONECTADA
void exibirInformacoes(){
    Serial.print(F("\n"));
    
    if (WiFi.status() == WL_CONNECTED)
        Serial.print(F("WIFI CONECTADO!\n"));
    else
        Serial.print(F("WIFI NÃO CONECTADO!\n"));
  
    Serial.print(F("ENDERECOIP: "));
    Serial.print(WiFi.localIP());
    Serial.print(F("\n"));
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
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(LED, OUTPUT);

    digitalWrite(LED_BUILTIN, LOW);
    digitalWrite(LED, ESTADO);
    
    // CONECTANDO À REDE DO OUTRO NODEMCU MASTER
    conectarRede("ProjetoSemaforo", "12345678");
    exibirInformacoes();
}


// FUNÇÃO PRINCIPAL DO PROGRAMA
void loop() {
    tcpCleanup();
    WiFiClient client = server.available();
  
    // ENQUANTO NÃO FOR CONECTADO NO SERVIDOR CLIENTE
    if (!client)
      return;
    
    // LENDO A REQUISIÇÃO RECEBIDA E AUMENTANDO i
    String requisicao = client.readStringUntil('\r');
    processaRequisicao(requisicao);
    
    paginaHTML(&client);
    client.flush();
    client.stop();
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
