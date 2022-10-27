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
int tempoVermelho, tempoResto, erro, nivelBateria;
bool estadoRaspberry, sinal, sinc;
unsigned long contagem;


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
    Serial.print("REQUISICAO: ");
    Serial.println(requisicao);

    if(requisicao.indexOf("RASPBERRY") != -1)
      estadoRaspberry = true;

    if(requisicao.indexOf("ATIVAR") != -1)
        sinal = true;
  
    if(requisicao.indexOf("DESATIVAR") != -1)
        sinal = false;

    if(requisicao.indexOf("SINC?") != -1)
        sincMode(requisicao);
}


// ATIVANDO OS LEDS PELO TEMPO DE SINAL
void handleSinc(void){
    if(!sinc)
        return;

    bool condicao = (sinal & millis() - contagem >= tempoVermelho) ||
                    (!sinal & millis() - contagem >= tempoResto);
    
    if(condicao){
        contagem = millis();
        sinal = !sinal;
    }
}


// FUNÇÃO PARA ATIVAR O MODO DE SINCRONIZAÇÃO SEM A CÂMERA
void sincMode(String req){
    int K0 = req.indexOf("?");        // PROCURA O PRIMEIRO "?"
    int K1 = req.indexOf("|", K0+1);  // PROCURA A PARTIR DE PRIMEIRO "|"
    int K2 = req.indexOf("|", K1+1);  // PROCURA A PARTIR DO SEGUNDO  "|"
    int K3 = req.indexOf("|", K2+1);  // PROCURA A PARTIR DO TERCEIRO "|"
    
    tempoVermelho = req.substring(K0+1, K1).toInt();
    tempoResto    = req.substring(K1+1, K2).toInt();
    erro          = req.substring(K2+1, K3).toInt();
    
    Serial.println(tempoVermelho);
    Serial.println(tempoResto);
    Serial.println(erro);
    Serial.println();

    // DESLIGANDO O RASPBERRY E ATUALIZANDO O SINAL PARA VERMELHO
    digitalWrite(RASPBERRY, LOW);
    estadoRaspberry = false;
    sinal = true;
    
    // NA PRIMEIRA ATIVAÇÃO TEMOS QUE CONSIDERAR O DELAY DE ERRO  
    digitalWrite(LED, sinal);
    delay(tempoVermelho-erro);

    sinal = false;
    sinc  = true;
    contagem = millis();
}


// ESTABELECENDO A COMUNICAÇÃO WIFI E MONITOR SERIAL
void setup() {
    Serial.begin(9600); 

    pinMode(LED, OUTPUT);
    pinMode(RASPBERRY, OUTPUT);
    pinMode(LED_BUILTIN, OUTPUT);
    
    digitalWrite(LED, LOW);
    digitalWrite(LED_BUILTIN, LOW);
    
    // CONECTANDO À REDE DO OUTRO NODEMCU MASTER
    conectarRede("ProjetoSemaforo", "12345678");
    exibirInformacoes();

    nivelBateria = 80;
    estadoRaspberry = false;
    sinal = false;
    sinc  = false;
}


// FUNÇÃO PRINCIPAL DO PROGRAMA
void loop(){
    tcpCleanup();
    handleSinc();

    digitalWrite(LED, sinal);
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
    (*cl).print("<p>DISPOSITIVO FUNCIONANDO</p>");

    (*cl).println("</body>");
    (*cl).println("</html>");
}
