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

// POIS SÃO ENVIADOS 2 SINAIS DE 0.2 SEGUNDOS ANTES DA ATIVAÇÃO
#define DELAY 500

// DECLARAÇÃO DA FUNÇÃO PARA CRIAÇÃO DE PÁGINA HTML
void paginaHTML(WiFiClient *cl);

// VARIÁVEIS GLOBAIS
int tempoVermelho;
int tempoResto;
int erro;
int nivelBateria;
bool estadoSinal = false;
bool modoSinal = false;
bool estadoRaspberry = false;


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
        estadoSinal = true;
        estadoRaspberry = true;
    }
  
    if(requisicao.indexOf("DESATIVAR") != -1){
        digitalWrite(LED, LOW);
        estadoSinal = false;
        estadoRaspberry = true;
    }

    if(requisicao.indexOf("SINC?") != -1){
        modoSinal = true;
        sincMode(requisicao);
        modoSinal = false;
    }
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
    
    tempoVermelho = req.substring(K0+1, K1).toInt();
    tempoResto    = req.substring(K1+1, K2).toInt();
    erro          = req.substring(K2+1, K3).toInt();
    
    Serial.println(tempoVermelho);
    Serial.println(tempoResto);
    Serial.println(erro);
    Serial.println();

    // NA PRIMEIRA ATIVAÇÃO TEMOS QUE CONSIDERAR O DELAY DE ERRO
    bool sinal = false;
    digitalWrite(LED, sinal);
    delay(tempoVermelho-DELAY-erro);
    
    digitalWrite(RASPBERRY, LOW);
    int tempo = millis();
    
    // MODO AUTOMÁTICO ONDE O DELAY DEPENDE DO ESTADO
    while(millis() - tempo < 600000)
        sinal = delaySemaforo(sinal, tempoVermelho, tempoResto);

    // LIGANDO O RASPBERRY NOVAMENTE
    digitalWrite(RASPBERRY, HIGH);

    // ESPERANDO O RASPBERRY LIGAR
    while(millis() - tempo < 60000)
        sinal = delaySemaforo(sinal, tempoVermelho, tempoResto);
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
  (*cl).println("<title>Site Semáforo</title>");
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
  (*cl).println("height: 50px;");
  (*cl).println("width:  200px;");
  (*cl).println("}");
  (*cl).println(".alinhado{");
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
  (*cl).println("<p class='alinhado' style='font-size: 20pt;'>&#128267;</p>");
  (*cl).println("<p class='alinhado'>Nível da Bateria:</p>");
  (*cl).println("<p class='alinhado'id='NivelBateria' class='emoji' style='color: blue;'>100%</p>");
  (*cl).println("<p class='alinhado' style='font-size: 22pt; margin-left: 70px;'>&#128678;</p>");
  (*cl).println("<p class='alinhado'>Estado do Semáforo: </p>");
  (*cl).println("<p class='alinhado'id ='EstadoSemaforo' class='emoji' style='color: red;'>VERMELHO</p>");
  (*cl).println("</div>");
  (*cl).println("<div id='botoes'>");
  (*cl).println("<input class='botoes' type='button' value='LIBERAR PASSAGEM' id='btnLigar' onclick='ativar()'>");
  (*cl).println("<input class='botoes' type='button' value='BARRAR PASSAGEM' id='btnDesligar' onclick='desativar()'>");
  (*cl).println("</div>");
  (*cl).println("<div class='info' style='text-align: center; margin-bottom: 30px;'>");
  (*cl).println("<p class='alinhado' style='font-size: 20pt;'>&#128214;</p>");
  (*cl).println("<p class='alinhado'>Informações</p>");
  (*cl).println("<p style='margin-bottom: -40px;'></p>");
  (*cl).println("<div class='alinhado' style='text-align: left; margin-right: 50px;'>");
  (*cl).println("<p class='alinhado'>Tempo Vermelhos: </p>");
  (*cl).println("<p class='alinhado' id='tempoVermelhos'>10 segundos</p>");
  (*cl).println("<p style='margin-top: -40px;'></p>");
  (*cl).println("<p class='alinhado'>Tempo Resto: </p>");
  (*cl).println("<p class='alinhado' id='tempoResto'>10 segundos</p>");
  (*cl).println("</div>");
  (*cl).println("<div class='alinhado' style='text-align: left;'>");
  (*cl).println("<p class='alinhado'>Modo Sinal: </p>");
  (*cl).println("<p class='alinhado' id='modo'>SÍNCRONO</p>");
  (*cl).println("<p style='margin-top: -40px;'></p>");
  (*cl).println("<p class='alinhado'>Estado Raspberry: </p>");
  (*cl).println("<p class='alinhado' id='func'>FUNCIONANDO</p>");
  (*cl).println("</div>");
  (*cl).println("</div>");
  (*cl).println("</section>");
  (*cl).println("<footer>");
  (*cl).println("<p> &copy; Projeto Semáforo </p>");
  (*cl).println("</footer>");
  (*cl).println("<script>");
  (*cl).println("function validarUsuario(usuario, senha){");
  (*cl).println("let user = window.prompt('digite o usuário: ')");
  (*cl).println("let password = window.prompt('digite a senha: ')");
  (*cl).println("if(user != usuario || password != senha){");
  (*cl).println("window.alert('usuário ou senha inválidos...')");
  (*cl).println("validarUsuario()");
  (*cl).println("}");
  (*cl).println("}");
  (*cl).println("function validarEstado(estadoSemaforo){");
  (*cl).println("txt = document.getElementById('EstadoSemaforo')");
  (*cl).println("if(estadoSemaforo){");
  (*cl).println("txt.innerHTML = 'VERMELHO'");
  (*cl).println("txt.style.color = 'red'");
  (*cl).println("return true");
  (*cl).println("}");
  (*cl).println("txt.innerHTML = 'NÃO VERMELHO'");
  (*cl).println("txt.style.color = 'blue'");
  (*cl).println("return false");
  (*cl).println("}");
  (*cl).println("function validarBateria(nivelBateria){");
  (*cl).println("txt = document.getElementById('NivelBateria')");
  (*cl).println("txt.innerHTML = nivelBateria + '%'");
  (*cl).println("}");
  (*cl).println("function validarTempos(tempoVermelhos, tempoResto){");
  (*cl).println("txt1 = document.getElementById('tempoVermelhos')");
  (*cl).println("txt2 = document.getElementById('tempoResto')");
  (*cl).println("txt1.innerText = tempoVermelhos/1000 + ' segundos'");
  (*cl).println("txt2.innerText = tempoResto/1000 + ' segundos'");
  (*cl).println("}");
  (*cl).println("function validarModo(modo){");
  (*cl).println("txt = document.getElementById('modo')");
  (*cl).println("if(modo){");
  (*cl).println("txt.innerHTML = 'SÍNCRONO'");
  (*cl).println("txt.style.color = 'blue'");
  (*cl).println("return true");
  (*cl).println("}");
  (*cl).println("txt.innerHTML = 'DETECTANDO'");
  (*cl).println("txt.style.color = 'red'");
  (*cl).println("return false");
  (*cl).println("}");
  (*cl).println("function validarFuncionamento(funcionamento){");
  (*cl).println("txt = document.getElementById('func')");
  (*cl).println("if(funcionamento){");
  (*cl).println("txt.innerHTML = 'NORMAL'");
  (*cl).println("txt.style.color = 'blue'");
  (*cl).println("return true");
  (*cl).println("}");
  (*cl).println("txt.innerHTML = 'SEM RESPOSTA'");
  (*cl).println("txt.style.color = 'red'");
  (*cl).println("return false");
  (*cl).println("}");
  (*cl).println("function ativar(){");
  (*cl).println("fetch('http://192.168.4.1/ATIVAR')");
  (*cl).println("fetch('http://192.168.4.3/ATIVAR')");
  (*cl).println("}");
  (*cl).println("function desativar(){");
  (*cl).println("fetch('http://192.168.4.1/DESATIVAR')");
  (*cl).println("fetch('http://192.168.4.3/DESATIVAR')");
  (*cl).println("}");
  
  (*cl).println("validarUsuario('projeto', 'semaforo')");
  (*cl).println("validarEstado(" + String(estadoSinal) + ")");
  (*cl).println("validarBateria(" + String(nivelBateria) + ")");
  (*cl).println("validarTempos(" + String(tempoVermelho/1000) + "," + String(tempoResto/1000) + ")");
  (*cl).println("validarModo(0)" + String(modoSinal) + ")");
  (*cl).println("validarFuncionamento(" + String(estadoRaspberry) +")");
  (*cl).println("</script>");
  (*cl).println("</body>");
  (*cl).println("</html>");
}
