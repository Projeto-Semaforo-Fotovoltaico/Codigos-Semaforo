#include <WiFi.h>
WiFiServer server(80);

#define LED 0
void paginaHTML(WiFiClient *cl);


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

    if(requisicao.indexOf("ATIVAR") != -1)
        digitalWrite(LED, HIGH);
  
    if(requisicao.indexOf("DESATIVAR") != -1)
        digitalWrite(LED, LOW);

    if(requisicao.indexOf("SINC?") != -1)
        sincMode(requisicao);
}


// FUNÇÃO PARA ATIVAR O MODO DE SINCRONIZAÇÃO SEM A CÂMERA
void sincMode(String req){
    int K0 = req.indexOf("?");        // PROCURA O PRIMEIRO "?"
    int K1 = req.indexOf("|", K0+1);  // PROCURA A PARTIR DE "?"
    int K2 = req.indexOf("|", K1+1);  // PROCURA A PARTIR DO PRIMEIRO "|"
    int K3 = req.indexOf("|", K2+1);  // PROCURA A PARTIR DO SEGUNDO  "|"
    
    int  tempoVermelho = req.substring(K0+1, K1).toInt();
    int  tempoResto    = req.substring(K1+1, K2).toInt();
    bool estado        = req.substring(K2+1, K3).toInt();
    
    Serial.println(tempoVermelho);
    Serial.println(tempoResto);
    Serial.println(estado);
    Serial.println();
  
    for(int x=0; x<100; x++){
        digitalWrite(LED, estado);
        delay(tempoVermelho);
        estado = !estado;

        digitalWrite(LED, estado);
        delay(tempoResto);
        estado = !estado;
    }
}


// ESTABELECENDO A COMUNICAÇÃO WIFI E MONITOR SERIAL
void setup() {
    Serial.begin(9600); 
    startServer("ProjetoSemaforo", "12345678");
    
    pinMode(LED, OUTPUT);
    digitalWrite(LED, LOW);
}


// FUNÇÃO PRINCIPAL DO PROGRAMA
void loop() {
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
  (*cl).println("<!DOCTYPE html>");
  (*cl).println("<html lang='pt-br'>");
  (*cl).println("<head>");
  (*cl).println("<meta charset='UTF-8'>");
  (*cl).println("<meta http-equiv='X-UA-Compatible' content='IE=edge'>");
  (*cl).println("<meta name='viewport' content='width=device-width, initial-scale=1.0'>");
  (*cl).println("<title>Exercício 3</title>");
  (*cl).println("<style>");
  (*cl).println("body{");
  (*cl).println("background-color: skyblue;");
  (*cl).println("font: normal 15pt Arial;");
  (*cl).println("text-align: center;");
  (*cl).println("}");
  (*cl).println("header{");
  (*cl).println("text-align: center;");
  (*cl).println("font: bold 18pt Arial;");
  (*cl).println("padding: 20px;");
  (*cl).println("width: 400px;");
  (*cl).println("height: 40px;");
  (*cl).println("line-height: 40px;");
  (*cl).println("margin: auto;");
  (*cl).println("color: black;");
  (*cl).println("background-color: yellow;");
  (*cl).println("border: 1px solid black;");
  (*cl).println("border-radius: 10px;");
  (*cl).println("}");
  (*cl).println("section{");
  (*cl).println("text-align: center;");
  (*cl).println("margin: auto;");
  (*cl).println("width: 750px;");
  (*cl).println("margin-top: 20px;");
  (*cl).println("padding: 20px;");
  (*cl).println("background-color: white;");
  (*cl).println("border: 1px solid black;");
  (*cl).println("border-radius: 10px;");
  (*cl).println("}");
  (*cl).println("footer{");
  (*cl).println("text-align: center;");
  (*cl).println("color: white;");
  (*cl).println("font: italic;");
  (*cl).println("}");
  (*cl).println("div{");
  (*cl).println("text-align: left;");
  (*cl).println("margin-bottom: -50px;");
  (*cl).println("}");
  (*cl).println("div#botoes{");
  (*cl).println("text-align: center;");
  (*cl).println("}");
  (*cl).println("input.botoes{");
  (*cl).println("margin: 50px;");
  (*cl).println("height:50px;");
  (*cl).println("width:200px;");
  (*cl).println("}");
  (*cl).println("p.emoji{");
  (*cl).println("display: inline-block;");
  (*cl).println("}");
  (*cl).println("</style>");
  (*cl).println("</head>");
  (*cl).println("<body>");
  (*cl).println("<header>");
  (*cl).println("SEMÁFORO PARA PEDESTRES");
  (*cl).println("</header>");
  (*cl).println("<section>");
  (*cl).println("<div class='info'>");
  (*cl).println("<p class='emoji' style='font-size: 20pt;'>&#128267;</p>");
  (*cl).println("<p class='emoji'>Nível da Bateria:</p>");
  (*cl).println("<p class='emoji' style='color: blue;'>100%</p>");
  (*cl).println("<p class='emoji' style='font-size: 22pt; margin-left: 100px;'>&#128678;</p>");
  (*cl).println("<p class='emoji'>Estado do Semáforo: </p>");
  (*cl).println("<p class='emoji' style='color: red;'>VERMELHO</p>");
  (*cl).println("</div>");
  (*cl).println("<div id='botoes'>");
  (*cl).println("<input class='botoes' type='button' value='LIBERAR PASSAGEM' id='btnLigar' onclick='ativar()'>");
  (*cl).println("<input class='botoes' type='button' value='BARRAR PASSAGEM' id='btnDesligar' onclick='desativar()'>");
  (*cl).println("</div>");
  (*cl).println("<div class='info' style='text-align: center; margin-bottom: -45px;'>");
  (*cl).println("<p class='emoji' style='font-size: 20pt;'>&#128214;</p>");
  (*cl).println("Histórico");
  (*cl).println("</div>");
  (*cl).println("<div id='historico' style='text-align: center; padding: 30px;'>");
  (*cl).println("<select name='lista' id='lisaHistorico' size='20'");
  (*cl).println("style='width: 250px;  height: 200px; border: 1px solid black; margin-bottom: 40px;'>");
  (*cl).println("<option>DETECTADO</option>");
  (*cl).println("<option>NÃO DETECTADO</option>");
  (*cl).println("<option>DETECTADO</option>");
  (*cl).println("<option>NÃO DETECTADO</option>");
  (*cl).println("<option>DETECTADO</option>");
  (*cl).println("<option>NÃO DETECTADO</option>");
  (*cl).println("<option>DETECTADO</option>");
  (*cl).println("<option>NÃO DETECTADO</option>");
  (*cl).println("<option>DETECTADO</option>");
  (*cl).println("<option>NÃO DETECTADO</option>");
  (*cl).println("<option>DETECTADO</option>");
  (*cl).println("<option>NÃO DETECTADO</option>");
  (*cl).println("<option>DETECTADO</option>");
  (*cl).println("<option>NÃO DETECTADO</option>");
  (*cl).println("<option>DETECTADO</option>");
  (*cl).println("<option>NÃO DETECTADO</option>");
  (*cl).println("<option>DETECTADO</option>");
  (*cl).println("<option>NÃO DETECTADO</option>");
  (*cl).println("<option>DETECTADO</option>");
  (*cl).println("<option>NÃO DETECTADO</option>");
  (*cl).println("</select>");
  (*cl).println("</div>");
  (*cl).println("</section>");
  (*cl).println("<footer>");
  (*cl).println("<p> &copy; Projeto Semáforo </p>");
  (*cl).println("</footer>");
  (*cl).println("<script>");
  (*cl).println("function validar(){");
  (*cl).println("let user = window.prompt('digite o usuário: ')");
  (*cl).println("let password = window.prompt('digite a senha: ')");
  (*cl).println("if(user != 'projeto' || password != 'semaforo'){");
  (*cl).println("window.alert('usuário ou senha inválidos...')");
  (*cl).println("validar()");
  (*cl).println("}");
  (*cl).println("}");
  (*cl).println("function ativar(){");
  (*cl).println("fetch('http://192.168.4.1/ATIVAR')");
  (*cl).println("fetch('http://192.168.4.3/ATIVAR')");
  (*cl).println("}");
  (*cl).println("function desativar(){");
  (*cl).println("fetch('http://192.168.4.1/DESATIVAR')");
  (*cl).println("fetch('http://192.168.4.3/DESATIVAR')");
  (*cl).println("}");
  (*cl).println("validar()");
  (*cl).println("</script>");
  (*cl).println("</body>");
  (*cl).println("</html>");
}
