// BIBLIOTECAS UTILIZADAS NESTE CÓDIGO
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>

#define PINO_DIGITAL   3
#define PINO_ANALOGICO 4

// PORTA PADRÃO PARA O SHIELD RECEBER AS REQUISIÇÕES DAS PÁGINAS
WiFiServer server(80);

// DECLARANDO AS FUNÇÕES SECUNDÁRIAS
void paginaHTML(WiFiClient client, String RequisicaoHTTP, bool currentLineIsBlack);


// CONECTANDO À REDE LOCAL PELO NOME E SENHA
bool conectarRede(char* nomeRede, char* senhaRede){
    WiFi.begin(nomeRede, senhaRede);

    while(WiFi.status() != WL_CONNECTED){
        delay(500);
        Serial.println("conectando...");
    }

    server.begin();
    return true;
}


// EXIBINDO INFORMAÇÕES DA REDE CONECTADA
void exibirInformacoes(){
    if (WiFi.status() == WL_CONNECTED)
        Serial.println("WIFI CONECTADO!");
    else
        Serial.println("WIFI NÃO CONECTADO!");
  
    Serial.print("ENDERECOIP: ");
    Serial.println(WiFi.localIP());
}


// PEGA UMA REQUISIÇÃO DO NAVEGADOR MANIPULANDO A STRING PELO SEU ENDEREÇO DE MEMÓRIA
String getURLRequest(String *requisicao) {
  int inicio, fim;
  String retorno;

  inicio = requisicao->indexOf("GET") + 3;
  fim = requisicao->indexOf("HTTP/") - 1;
  retorno = requisicao->substring(inicio, fim);
  retorno.trim();

  return retorno;
}


// VERIFICA QUE A REQUISIÇÃO É DA PÁGINA PRINCIPAL DO SERVIDOR
bool mainPageRequest(String *requisicao) {
    String valor;
    bool retorno = false;

    valor = getURLRequest(requisicao);
    valor.toLowerCase();
    
    if (valor == "/") {
       retorno = true;
    }
    
    if (valor.substring(0,2) == "/?") {
       retorno = true;
    }  
    
    if (valor.substring(0,10) == "/index.htm") {
       retorno = true;
    }  
    
    return retorno;
}


// CONFIGURAÇÕES PRINCPAIS NODEMCU
void setup(){
    Serial.begin(115200);
    conectarRede("Klauss", "KlaussSenha");
    exibirInformacoes();
}


// FUNÇÃO PRINCIPAL EM LOOP INFINITO
void loop(){
    // VARIÁVEIS LOCAIS PARA CONFIGURAÇÃO DO SERVIDOR E REQUISIÇÃO
    WiFiClient client = server.available();
    String RequisicaoHTTP = "";
    String valorURL = "";

    // LOOP INFINITO ENQUANTO O SERVIDOR CLIENTE NÃO FOR CONECTADO
    if (!client)
        return;

    bool currentLineIsBlank = true;
    
    // ENQUANTO ESTIVERMOS CONECTADOS AO SERVIDOR CLIENTE
    while(client.connected()){
        if (!client.available())                            // LOOP INFINITO ATÉ O SERVIDOR CLIENTE ESTAR DISPONÍVEL
            continue;

        char C = client.read();                             // LENDO AS LINHAS DE REQUISIÇÃO DO SERVIDOR CLIENTE
        RequisicaoHTTP += C;                                // ARMAZENANDO CADA CARACTERE EM REQUISICAO HTTP

        if(C == '\n' && currentLineIsBlank){
            String valorURL;;

            // VERIFICA SE ESTÁ RECEBENDO UMA REQUISIÇÃO DA PÁGINA PRINCIPAL (CONFIGURAÇÃO DA PÁGINA HTML)
            if (mainPageRequest(&RequisicaoHTTP)){
                valorURL = getURLRequest(&RequisicaoHTTP);  // PROCESSANDO O URL PRINCIPAL
                Serial.println(RequisicaoHTTP);             // MOSTRANDO O PACOTE RECEBIDO DO SERVIDOR HTTP

                // ENVIANDO AO NAVEGADOR AS SEGUINTES CONFIGURAÇÕES
                client.println("HTPP/1.1 200 OK");
                client.println("Content-Type: text/html");
                client.println("Connection: keep-alive");
                client.println();

                // IMPRIMINDO O CÓDIGO HTML PARA MONTAR A PÁGINA ATRAVÉS DA FUNÇÃO
                paginaHTML(client, RequisicaoHTTP, currentLineIsBlank);

                // ENCERRANDO A CONEXÃO COM O SERVIDOR CLIENTE
                delay(1);
                client.stop();
            }
            
            // QUANDO O JAVASCRIPT SOLICITAR PARA O ESP8266 A ATUALIZAÇÃO DOS DADOS, ISSO SERÁ ENVIADO (ATUALIZAÇÃO DOS PINOS)
            else if(RequisicaoHTTP.indexOf("solicitacao_via_ajax") > -1){
                
            }

            // PARA RESPONDER QUALQUER OUTRA REQUISIÇÃO DO NAVEGADOR
            else{
                Serial.println(RequisicaoHTTP);
                client.println("HTTP/1.1 200 OK");
            }

            RequisicaoHTTP = "";    
            break;
        }

        if (C == '\n')  
            currentLineIsBlank = true;
        else if (C != '\r')
            currentLineIsBlank = false;
    }
}

// MONTANDO A PÁGINA HTML
void paginaHTML(WiFiClient client, String RequisicaoHTTP, bool currentLineIsBlank){
    
}
