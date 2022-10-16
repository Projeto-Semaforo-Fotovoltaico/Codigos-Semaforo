#include <lwip/priv/tcp_priv.h>

// LIMPANDO MEMÓRIA FLASH
void tcpCleanup(){
  while (tcp_tw_pcbs != NULL)
    tcp_abort(tcp_tw_pcbs);
}


#include <ESP8266WiFi.h>
WiFiServer server(80);

// PINO DIGITAL CONECTADO AO RELÉ DAS LÂMPADAS E AO RASPBERRY
#define LED D0
#define RASPBERRY D1


// DECLARAÇÃO DA FUNÇÃO PARA CRIAÇÃO DE PÁGINA HTML
void paginaHTML(WiFiClient *cl);

// VARIÁVEIS GLOBAIS
int tempoVermelho;
int tempoResto;
int erro;
int nivelBateria;
bool estadoRaspberry = false;

int contagem;
bool sinal = false;
bool sinc = false;


// CRIANDO E INICIANDO O ROTEADOR LOCAL
void startServer(char* nome, char* senha){
    IPAddress staticIP(192, 168, 4, 2);  // IP ESTÁTICO
    IPAddress gateway(192, 168, 4, 1);   // GATEWAY ESTÁTICO IP
    IPAddress subnet(255, 255, 255, 0);  // OCULTAR SUB REDE
  
    // MODO DE TRABALHO WIFI VIA ACESS POINT
    WiFi.mode(WIFI_AP);                 
    WiFi.softAP(nome, senha);
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

    if(requisicao.indexOf("ATIVAR") != -1){
        digitalWrite(LED, HIGH);
        sinal = true;
        estadoRaspberry = true;
    }
  
    if(requisicao.indexOf("DESATIVAR") != -1){
        digitalWrite(LED, LOW);
        sinal = false;
        estadoRaspberry = true;
    }

    if(requisicao.indexOf("SINC?") != -1){
        sinc = true;
        sincMode(requisicao);
    }
}


// ATIVANDO OS LEDS PELO TEMPO DE SINAL
void handleSinc(void){
  if(!sinc)
    return;
  
  if(sinal)
    digitalWrite(LED, HIGH);
  else
    digitalWrite(LED, LOW);
  
  
  if(sinal & millis() - contagem > tempoVermelho){
    contagem = millis();
    sinal = !sinal;
  }
  
  if(!sinal & millis() - contagem > tempoResto){
    contagem = millis();
    sinal = !sinal;
  }
}


// FUNÇÃO PARA ATIVAR O MODO DE SINCRONIZAÇÃO SEM A CÂMERA
void sincMode(String req){
    int K0 = req.indexOf("?");        // PROCURA O PRIMEIRO "?"
    int K1 = req.indexOf("|", K0+1);  // PROCURA A PARTIR DE "?"
    int K2 = req.indexOf("|", K1+1);  // PROCURA A PARTIR DO PRIMEIRO "|"
    int K3 = req.indexOf("|", K2+1);  // PROCURA A PARTIR DO SEGUNDO  "|"
    
    tempoVermelho = req.substring(K0+1, K1).toInt();
    tempoResto    = req.substring(K1+1, K2).toInt();
    erro          = req.substring(K2+1, K3).toInt();
    
    Serial.println(tempoVermelho);
    Serial.println(tempoResto);
    Serial.println(erro);
    Serial.println();

    digitalWrite(RASPBERRY, LOW);
    sinal = false;
    sinc  = false;
    
    // NA PRIMEIRA ATIVAÇÃO TEMOS QUE CONSIDERAR O DELAY DE ERRO  
    digitalWrite(LED, sinal);
    delay(tempoVermelho-erro);
    
    sinal = true;
    sinc  = true;
    contagem = millis();
}


// ESTABELECENDO A COMUNICAÇÃO WIFI E MONITOR SERIAL
void setup() {
    Serial.begin(9600); 
    startServer("ProjetoSemaforo", "12345678");
    
    pinMode(LED, OUTPUT);
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(RASPBERRY, OUTPUT);
    
    digitalWrite(LED, LOW);
    digitalWrite(RASPBERRY, HIGH);
    digitalWrite(LED_BUILTIN, LOW);
}


// FUNÇÃO PRINCIPAL DO PROGRAMA
void loop() {
    tcpCleanup();
    handleSinc();
    WiFiClient client = server.available();
  
    // ENQUANTO NÃO FOR CONECTADO NO SERVIDOR CLIENTE
    if (!client)
      return;
    
    // LENDO A REQUISIÇÃO RECEBIDA E AUMENTANDO i
    String requisicao = client.readStringUntil('\r'); 
    processaRequisicao(requisicao);

    // SE FOR CHAMADO A PÁGINA DE MENU PRINCIPAL
    if(requisicao.indexOf("/MENU") != -1)
        paginaHTML(&client);

    // LIMPANDO O LIXO GERADO PELA REQUISIÇÃO E ENCERRANDO
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
    (*cl).println("LOW</p>");

    (*cl).println("</body>");
    (*cl).println("</html>");
}
