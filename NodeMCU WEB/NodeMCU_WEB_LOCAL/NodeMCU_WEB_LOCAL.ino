// BIBLIOTECAS UTILIZADAS NESTE CÓDIGO
#include <ESP8266WiFi.h>

#define PINO_DIGITAL  2
bool ESTADO = 0;

// PORTA PADRÃO PARA O SHIELD RECEBER AS REQUISIÇÕES DAS PÁGINAS
WiFiServer server(80);
void paginaHTML(WiFiClient *cl);


// CONECTANDO À REDE LOCAL PELO NOME E SENHA
void conectarRede(char* nomeRede, char* senhaRede){
    WiFi.mode(WIFI_STA);
    WiFi.begin(nomeRede, senhaRede);

    while(WiFi.status() != WL_CONNECTED){
        delay(500);
        Serial.print(F("."));
    }

    server.begin();
}


// EXIBINDO INFORMAÇÕES DA REDE CONECTADA
void exibirInformacoes(){
    Serial.print("\n");
    
    if (WiFi.status() == WL_CONNECTED)
        Serial.println("WIFI CONECTADO!");
    else
        Serial.println("WIFI NÃO CONECTADO!");
  
    Serial.print("ENDERECOIP: ");
    Serial.print(WiFi.localIP());
    Serial.print("\n");
}


// CASO DESCONECTE COM A REDE, FAÇA A RECONEXÃO
void reconectarRede(void){
  if ((WiFi.status() != WL_CONNECTED)) {
      Serial.print(millis());
      Serial.printkb("Reconnecting to WiFi...");
      WiFi.disconnect();
      WiFi.reconnect();
    }
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


// FUNÇÃO PRINCIPAL EM LOOP INFINITO
void loop(){
    reconectarRede();
    WiFiClient client = server.available();

    // LOOP INFINITO ENQUANTO O SERVIDOR CLIENTE NÃO FOR CONECTADO
    if (!client)
        return;

    // LOOP INFINITO ENQUANTO O SERVIDOR CLIENTE NÃO ESTIVER DISPONÍVEL
    while(!client.available())
      delay(1);
    
    String requisicao = client.readStringUntil('\r');
    Serial.print("REQUISICAO: ");
    Serial.println(requisicao); 


    if(requisicao.indexOf("/") != -1){
        Serial.println("MONTANDO PÁGINA HTML!");
    }
    
    if(requisicao.indexOf("POST") != -1){
        Serial.println("ATIVANDO O BOTAO!");
        ESTADO = !ESTADO;
        digitalWrite(PINO_DIGITAL, ESTADO);
    }

    paginaHTML(&client);

    client.flush();
    client.stop();
    delay(1);
}

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

    
    (*cl).println("<form action='' method='post'>");
    (*cl).println("<button name='foo' value='upvote'>ATIVAR</button>");
    (*cl).println("</form>");
    
    //(*cl).println("<a href='#ativarBotao'><button>BOTAO</button></a>");
    
    (*cl).print("<p>GPIO is now ");
    
    if (ESTADO)
        (*cl).println("HIGH</p>");
    else
        (*cl).println("LOW</p>");

    (*cl).println("</body>");
    (*cl).println("</html>");
}
