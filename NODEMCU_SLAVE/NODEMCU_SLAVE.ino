#include <lwip/priv/tcp_priv.h>

// LIMPANDO MEMÓRIA FLASH
void tcpCleanup(){
  while (tcp_tw_pcbs != NULL)
    tcp_abort(tcp_tw_pcbs);
}


#include <ESP8266WiFi.h>
WiFiServer server(80);

// PINO DIGITAL CONECTADO AO RELÉ DAS LÂMPADAS
#define LED D0

// POIS SÃO ENVIADOS 2 SINAIS DE 0.2 SEGUNDOS ANTES DA ATIVAÇÃO
#define DELAY 300

// DECLARAÇÃO DA FUNÇÃO PARA CRIAÇÃO DE PÁGINA HTML
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
        digitalWrite(LED, HIGH);
  
    if(requisicao.indexOf("DESATIVAR") != -1)
        digitalWrite(LED, LOW);

    if(requisicao.indexOf("SINC?") != -1)
        sincMode(requisicao);
}


// ATIVANDO OS LEDS PELO DELAY DE SINAL
bool delaySemaforo(bool sinal, int tempoVermelho, int tempoResto){
  digitalWrite(LED, sinal);
        
  if(sinal)
    delay(tempoVermelho);
  else
    delay(tempoResto);
    
  return !sinal;
}


// FUNÇÃO PARA ATIVAR O MODO DE SINCRONIZAÇÃO SEM A CÂMERA
void sincMode(String req){
    int K0 = req.indexOf("?");        // PROCURA O PRIMEIRO "?"
    int K1 = req.indexOf("|", K0+1);  // PROCURA A PARTIR DE "?"
    int K2 = req.indexOf("|", K1+1);  // PROCURA A PARTIR DO PRIMEIRO "|"
    int K3 = req.indexOf("|", K2+1);  // PROCURA A PARTIR DO SEGUNDO  "|"
    
    int tempoVermelho = req.substring(K0+1, K1).toInt();
    int tempoResto    = req.substring(K1+1, K2).toInt();
    int erro          = req.substring(K2+1, K3).toInt();
    
    Serial.println(tempoVermelho);
    Serial.println(tempoResto);
    Serial.println(erro);
    Serial.println();

    // NA PRIMEIRA ATIVAÇÃO TEMOS QUE CONSIDERAR O DELAY DE ERRO
    bool sinal = false;
    digitalWrite(LED, sinal);
    
    delay(tempoVermelho-DELAY-erro);
    int tempo = millis();
    
    // MODO AUTOMÁTICO ONDE O DELAY DEPENDE DO ESTADO
    while(millis() - tempo < 600000)
        sinal = delaySemaforo(sinal, tempoVermelho, tempoResto);

    // ESPERANDO O RASPBERRY LIGAR
    for(int x=0; x<5; x++)
        sinal = delaySemaforo(sinal, tempoVermelho, tempoResto);
}


// ESTABELECENDO A COMUNICAÇÃO WIFI E MONITOR SERIAL
void setup() {
    Serial.begin(9600); 
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(LED, OUTPUT);

    digitalWrite(LED_BUILTIN, LOW);
    digitalWrite(LED, LOW);
    
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
    
    // SE FOR CHAMADO QUALQUER REQUISIÇÃO, IMPRIMA UMA RESPOSTA
    if(requisicao.indexOf("/") != -1)
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
    (*cl).println("LOW</p>");

    (*cl).println("</body>");
    (*cl).println("</html>");
}
