// USAR ESP32 WROVER MODULE
#include <WebServer.h> // INSTALADO POR PADRÃO
#include <WiFi.h>      // INSTALADO POR PADRÃO
#include <esp32cam.h>  // BAIXAR E IMPORTAR ARQUIVO ZIP

// INICIANDO O OBJETO PARA SERVIDOR LOCAL DO ROTEADOR
WebServer server(80);

// CONFIGURAÇÃO DAS RESOLUÇÕES
static auto loRes = esp32cam::Resolution::find(320, 240);
static auto hiRes = esp32cam::Resolution::find(800, 600);


// CONFIGURANDO E INICIANDO CAMERA
void configurarCamera(){
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(hiRes);
    cfg.setBufferCount(2);
    cfg.setJpeg(80);
  
    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
}


// CONECTANDO E CONFIGURANDO WIFI
void startServer(char *nome, char *senha){
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(nome, senha);

  // (OPCIONAL) CONFIGURAÇÕES SECUNDÁRIAS DO SERVIDOR LOCAL
  IPAddress staticIP(192, 168, 4, 4);     // IP ESTÁTICO (USADO PARA EXTRAIR AS IMAGENS)
  IPAddress gateway(192, 168, 4, 2);      // GATEWAY ESTÁTICO IP 
  IPAddress subnet(255, 255, 255, 0);     // OCULTAR SUB REDE
  WiFi.config(staticIP, gateway, subnet);
  
  while (WiFi.status() != WL_CONNECTED){
    Serial.print(".");
    delay(500);
  }

  Serial.println();
}


// IMPRIMINDO INFORMAÇÕES DO SERVIDOR CRIADO PARA ACESSAR A CÂMERA
void exibirInformacoes(){
  Serial.print("http://");
  Serial.println(WiFi.localIP());

  Serial.println("  /cam.bmp");
  Serial.println("  /cam-lo.jpg");
  Serial.println("  /cam-hi.jpg");
  Serial.println("  /cam.mjpeg");
}


// RESETANDO O ESP32 EM CASO DE FALHAS
void resetarESP(){
  Serial.println("RESETANDO ESP");
  ESP.restart();
}


// CASO DESCONECTE COM A REDE, FAÇA A RECONEXÃO
void reconectarRede(void){
  if ((WiFi.status() != WL_CONNECTED)){
      delay(10000);
      resetarESP();
  }
}


// CONFIGURAÇÕES PRINCIPAIS
void setup(){
  Serial.begin(9600);
  Serial.println();
  
  configurarCamera();
  startServer("ProjetoSemaforo", "12345678");
  exibirInformacoes();

  // COMANDOS PARA CHAMAR AS FUNÇÕES PARA AS RESPECTIVAS REQUISIÇÕES
  server.on("/cam.bmp", handleBmp);
  server.on("/cam-lo.jpg", handleJpgLo);
  server.on("/cam-hi.jpg", handleJpgHi);
  server.on("/cam.jpg", handleJpg);
  server.on("/cam.mjpeg", handleMjpeg);

  server.on("/RESET", resetarESP);
  server.begin();
}


// LOOP PRINCIPAL
void loop(){
    reconectarRede();
    server.handleClient();
}


// ENVIANDO ARQUIVOS DE IMAGEM BMP
void handleBmp(){
    if (!esp32cam::Camera.changeResolution(loRes)) {
      Serial.println("SET-LO-RES FAIL");
    }
  
    auto frame = esp32cam::capture();
    if (frame == nullptr) {
      Serial.println("CAPTURE FAIL");
      server.send(503, "", "");
      return;
    }
    Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                  static_cast<int>(frame->size()));
  
    if (!frame->toBmp()) {
      Serial.println("CONVERT FAIL");
      server.send(503, "", "");
      return;
    }
    
    Serial.printf("CONVERT OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                  static_cast<int>(frame->size()));
  
    server.setContentLength(frame->size());
    server.send(200, "image/bmp");
    WiFiClient client = server.client();
    frame->writeTo(client);
}


// ENVIANDO ARQUIVOS DE IMAGEM JPG
void serveJpg(){
    auto frame = esp32cam::capture();
    if (frame == nullptr) {
        Serial.println("CAPTURE FAIL");
        server.send(503, "", "");
        return;
    }
    
    Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                  static_cast<int>(frame->size()));
  
    server.setContentLength(frame->size());
    server.send(200, "image/jpeg");
    WiFiClient client = server.client();
    frame->writeTo(client);
}


// ENVIANDO ARQUIVOS DE IMAGEM JPGLO
void handleJpgLo(){
    if (!esp32cam::Camera.changeResolution(loRes)) {
      Serial.println("SET-LO-RES FAIL");
    }
    serveJpg();
}


// RECEBIMENTO DE UMA REQUISIÇÃO PARA ENVIAR UM ARQUIVO JPG
void handleJpgHi(){
    if (!esp32cam::Camera.changeResolution(hiRes)) {
      Serial.println("SET-HI-RES FAIL");
    }
    serveJpg();
}


// FUNÇÃO AUXILIAR PARA ARQUIVOS JPG
void handleJpg(){
    server.sendHeader("Location", "/cam-hi.jpg");
    server.send(302, "", "");
}


// FUNÇÃO AUXILIAR PARA ARQUIVOS JPEG
void handleMjpeg(){
    if (!esp32cam::Camera.changeResolution(hiRes)) {
      Serial.println("SET-HI-RES FAIL");
    }
  
    Serial.println("STREAM BEGIN");
    WiFiClient client = server.client();
    auto startTime = millis();
    int res = esp32cam::Camera.streamMjpeg(client);
    if (res <= 0) {
      Serial.printf("STREAM ERROR %d\n", res);
      return;
    }
    auto duration = millis() - startTime;
    Serial.printf("STREAM END %dfrm %0.2ffps\n", res, 1000.0 * res / duration);
}
