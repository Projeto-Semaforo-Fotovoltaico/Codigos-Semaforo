#include <WiFi.h>
#include <ArduinoOTA.h>
#include <esp_timer.h>

WiFiServer server(80);

// PINO DIGITAL CONECTADO AO RELÉ DAS LÂMPADAS E AO RASPBERRY
#define LED 5
#define BUZZER 19

// DECLARAÇÃO DAS FUNÇÕES DO PROGRAMA
void paginaHTML(WiFiClient *cl);
void apitar(void);
void processaRequisicao(String requisicao);
void sincMode(String req);
void handleSinc(void);

// VARIÁVEIS GLOBAIS
int tempoVermelho, tempoResto, erro, nivelBateria;
bool estadoRaspberry, sinal, sinc;
unsigned long contagem;


// CONECTANDO À REDE LOCAL PELO NOME E SENHA
void conectarRede(char* nomeRede, char* senhaRede){
    WiFi.mode(WIFI_STA);
    WiFi.begin(nomeRede, senhaRede);

    // (OPCIONAL) CONFIGURAÇÕES SECUNDÁRIAS DO SERVIDOR LOCAL
    IPAddress staticIP(192, 168, 4, 3);     // IP ESTÁTICO (REQUISIÇÕES)
    IPAddress gateway(192, 168, 4, 11);     // GATEWAY ESTÁTICO IP
    IPAddress subnet(255, 255, 255, 0);     // OCULTAR SUB REDE
    WiFi.config(staticIP, gateway, subnet);

    while(WiFi.status() != WL_CONNECTED){
        delay(500);
        Serial.print(".");
    }

    server.begin();
    Serial.println();
    
    if (WiFi.status() == WL_CONNECTED)
        Serial.println("WIFI CONECTADO!");
    else
        Serial.println("WIFI NÃO CONECTADO!");
  
    Serial.print("ENDERECOIP: ");
    Serial.println(WiFi.localIP());
}


// PROCESSANDO A REQUISIÇÃO RECEBIDA PARA ACENDER OS LEDS
void processaRequisicao(String requisicao){
    Serial.print("REQUISICAO: ");
    Serial.println(requisicao);

    if(requisicao.indexOf("DESATIVAR") != -1){
        sinal = false;
        apitar();
    }

    else if(requisicao.indexOf("ATIVAR") != -1){
        sinal = true;
        apitar();
    }

    else if(requisicao.indexOf("APITAR") != -1)
        apitar();

    else if(requisicao.indexOf("SINC?") != -1)
        sincMode(requisicao);
}


// CONFIGURANDO O OTA (ATUALIZAÇÃO DE FIRMWARE VIA WIFI)
void setupOTA(const char* hostname, const char* password){
    ArduinoOTA.setHostname(hostname);
    ArduinoOTA.setPassword(password);

    ArduinoOTA.onStart([]() {
        Serial.println("Iniciando atualizacao...");
    });

    ArduinoOTA.onEnd([]() {
        Serial.println("Atualizacao concluida!");
    });

    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
        Serial.printf("Progresso: %u%%\r", (progress / (total / 100)));
    });

    ArduinoOTA.onError([](ota_error_t error) {
        Serial.printf("Erro[%u]: ", error);

        if (error == OTA_AUTH_ERROR)
            Serial.println("Falha na autenticacao");
        else if (error == OTA_BEGIN_ERROR)
            Serial.println("Falha no inicio da atualizacao");
        else if (error == OTA_CONNECT_ERROR)
            Serial.println("Falha na conexao");
        else if (error == OTA_RECEIVE_ERROR)
            Serial.println("Falha na recepcao");
        else if (error == OTA_END_ERROR)
            Serial.println("Falha no fim da atualizacao");
    });

    ArduinoOTA.begin();
    Serial.println("OTA pronto");
}


// ATIVANDO OS LEDS PELO TEMPO DE SINAL
void handleSinc(void){
    if(!sinc)
        return;

    unsigned long tempoAtual = esp_timer_get_time()/1000;
    unsigned long tempoDecorrido = tempoAtual - contagem;

    bool condicao = (sinal  && tempoDecorrido >= tempoVermelho) ||
                    (!sinal && tempoDecorrido >= tempoResto);
    
    if(condicao){
        sinal = !sinal;
        contagem = tempoAtual;
        apitar();
    }
}


// FUNÇÃO PARA ATIVAR O MODO DE SINCRONIZAÇÃO SEM A CÂMERA
void sincMode(String req){
    int K0 = req.indexOf("?");        // PROCURA O PRIMEIRO "?"
    int K1 = req.indexOf("A", K0+1);  // PROCURA A PARTIR DE PRIMEIRO "|"
    int K2 = req.indexOf("A", K1+1);  // PROCURA A PARTIR DO SEGUNDO  "|"
    int K3 = req.indexOf("A", K2+1);  // PROCURA A PARTIR DO TERCEIRO "|"
    
    tempoVermelho = req.substring(K0+1, K1).toInt();
    tempoResto    = req.substring(K1+1, K2).toInt();
    erro          = req.substring(K2+1, K3).toInt();
    
    Serial.println(tempoVermelho);
    Serial.println(tempoResto);
    Serial.println(erro);
    Serial.println();
    
    // NA PRIMEIRA ATIVAÇÃO TEMOS QUE CONSIDERAR O DELAY DE ERRO  
    sinal = true;
    digitalWrite(LED, sinal);
    delay(tempoVermelho-erro);

    sinal = false;
    sinc  = true;
    contagem = esp_timer_get_time()/1000;
}


// FUNÇÃO PARA ATIVAR O BUZZER EM UM CERTO INTERVALO PADRONIZADO
void apitar(){
  tone(BUZZER, 1000);
  delay(400);
  noTone(BUZZER);
}


// RECONECTAR REDE CASO PERCA A CONEXÃO
void reconectarRede(void){
    if (WiFi.status() != WL_CONNECTED)
        conectarRede("ProjetoSemaforo", "12345678");
}


// ESTABELECENDO A COMUNICAÇÃO WIFI E MONITOR SERIAL
void setup() {
    Serial.begin(9600); 
    conectarRede("ProjetoSemaforo", "12345678");
    setupOTA("ProjetoSemaforo", "12345678");

    nivelBateria = 80;
    sinal = false;
    sinc  = false;
    
    pinMode(LED, OUTPUT);
    digitalWrite(LED, LOW);
    apitar();
}


// FUNÇÃO PRINCIPAL DO PROGRAMA
void loop(){
    ArduinoOTA.handle();
    reconectarRede();

    handleSinc();
    digitalWrite(LED, sinal);
    
    WiFiClient client = server.available();
    client.setTimeout(5000);
  
    // ENQUANTO NÃO FOR CONECTADO NO SERVIDOR CLIENTE
    if (!client)
        return;

    // SE O SERVIDOR CLIENTE NÃO ESTIVER DISPONÍVEL
    if(!client.available())
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
    (*cl).print("<p>DISPOSITIVO FUNCIONANDO</p>");

    (*cl).println("</body>");
    (*cl).println("</html>");
}
