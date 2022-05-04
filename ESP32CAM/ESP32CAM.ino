#include <WebServer.h> // INSTALADO POR PADRÃO
#include <WiFi.h>      // INSTALADO POR PADRÃO
#include <esp32cam.h>  // BAIXAR E IMPORTAR ARQUIVO ZIP

const char* WIFI_SSID = "ProjetoSemaforo";    // NOME DA REDE WIFI
const char* WIFI_PASS = "12345678";           // SENHA DA REDE WIFI

// INICIANDO O OBJETO PARA SERVIDOR LOCAL DO ROTEADOR
WebServer server(80);


// CONFIGURAÇÃO DAS RESOLUÇÕES
static auto loRes = esp32cam::Resolution::find(320, 240);
static auto hiRes = esp32cam::Resolution::find(800, 600);


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


void setup(){
  Serial.begin(9600);
  Serial.println();

  // CONFIGURANDO E INICIANDO CAMERA
  {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(hiRes);
    cfg.setBufferCount(2);
    cfg.setJpeg(80);

    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
  }

  // CONECTANDO WIFI
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  // IMPRIMINDO INFORMAÇÕES DO SERVIDOR CRIADO
  Serial.print("http://");
  Serial.println(WiFi.localIP());
  Serial.println("  /cam.bmp");
  Serial.println("  /cam-lo.jpg");
  Serial.println("  /cam-hi.jpg");
  Serial.println("  /cam.mjpeg");

  // COMANDOS PARA CHAMAR AS FUNÇÕES PARA AS RESPECTIVAS REQUISIÇÕES
  server.on("/cam.bmp", handleBmp);
  server.on("/cam-lo.jpg", handleJpgLo);
  server.on("/cam-hi.jpg", handleJpgHi);
  server.on("/cam.jpg", handleJpg);
  server.on("/cam.mjpeg", handleMjpeg);

  // INICIANDO O SERVIDOR
  server.begin();
}


// CASO DESCONECTE COM A REDE, FAÇA A RECONEXÃO
void reconectarRede(void){
  if ((WiFi.status() != WL_CONNECTED)) {
      ESP.restart();
    }
}


// LOOP PRINCIPAL
void loop(){
  reconectarRede();
  server.handleClient();
}
