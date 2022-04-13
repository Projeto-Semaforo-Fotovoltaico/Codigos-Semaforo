#include <lwip/priv/tcp_priv.h>
#include <ESP8266WiFi.h>

WiFiServer server(80);
#define LED 14

bool ESTADO = 0;
void paginaHTML(WiFiClient *cl);


// LIMPANDO MEMÓRIA FLASH
void tcpCleanup(){
  while (tcp_tw_pcbs != NULL)
    tcp_abort(tcp_tw_pcbs);
}

// CRIANDO E INICIANDO O ROTEADOR LOCAL
void startServer(char* nome, char* senha){
  IPAddress staticIP(192, 168, 4, 3);  // IP ESTÁTICO
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


// ESTABELECENDO A COMUNICAÇÃO WIFI E MONITOR SERIAL
void setup() {
  Serial.begin(9600); 
  startServer("ProjetoSemaforo", "12345678");

  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(LED, OUTPUT);

  digitalWrite(LED_BUILTIN, LOW);
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
    delay(1);
  
  // LENDO A REQUISIÇÃO RECEBIDA
  String requisicao = client.readStringUntil('\r');
  Serial.print(F("REQUISICAO: "));
  Serial.println(requisicao); 

  if(requisicao.indexOf("/") != -1){
     Serial.print(F("MONTANDO PÁGINA HTML!\n"));
     paginaHTML(&client);
  }
    
  if(requisicao.indexOf("ATIVAR") != -1){
     Serial.print(F("ATIVANDO O LED!\n"));
     ESTADO = !ESTADO;
     digitalWrite(LED, HIGH);
     delay(1000);
     digitalWrite(LED, LOW);
  }

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
