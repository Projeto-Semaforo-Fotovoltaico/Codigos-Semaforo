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
  
    bool camera = Camera.begin(cfg);

    if (camera)
      Serial.println("CAMERA WORKING");
    else
      Serial.println("CAMERA FAIL");
}


// CONECTANDO E CONFIGURANDO WIFI
void startServer(char *nome, char *senha){
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(nome, senha);

  // (OPCIONAL) CONFIGURAÇÕES SECUNDÁRIAS DO SERVIDOR LOCAL
  IPAddress staticIP(192, 168, 4, 4);       // IP ESTÁTICO (USADO PARA EXTRAIR AS IMAGENS)
  IPAddress gateway(192, 168, 4, 12);       // GATEWAY ESTÁTICO IP 
  IPAddress subnet(255, 255, 255, 0);       // OCULTAR SUB REDE
  WiFi.config(staticIP, gateway, subnet);
  
  while (WiFi.status() != WL_CONNECTED){
    Serial.print(".");
    delay(500);
  }

  Serial.println();
}


// IMPRIMINDO INFORMAÇÕES DO SERVIDOR CRIADO PARA ACESSAR A CÂMERA
void exibirInformacoes(){
  Serial.print("ENDEREÇO:   http://");
  Serial.print(WiFi.localIP());
  Serial.println("/cam-hi.jpg");
}


// CASO DESCONECTE COM A REDE, RESETAR O ESP
void reconectarRede(void){
  if (WiFi.status() == WL_CONNECTED)
    return;

  delay(10000);
  Serial.println("RESETANDO ESP");
  ESP.restart();
}


// CONFIGURAÇÕES PRINCIPAIS
void setup(){
  Serial.begin(9600);
  Serial.println();
  
  configurarCamera();
  startServer("ProjetoSemaforo", "12345678");
  exibirInformacoes();

  server.on("/cam-hi.jpg", sendJPG);
  server.begin();
}


// LOOP PRINCIPAL
void loop(){
    reconectarRede();
    server.handleClient();
}


// RECEBIMENTO DE UMA REQUISIÇÃO PARA ENVIAR UM ARQUIVO JPG
void sendJPG(){
    if (!esp32cam::Camera.changeResolution(hiRes))
      Serial.println("SET-HI-RES FAIL");

    auto frame = esp32cam::capture();

    if (frame == nullptr) {
        Serial.println("CAPTURE FAIL");
        server.send(503, "", "");
        return;
    }
    
    Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(), static_cast<int>(frame->size()));
    server.setContentLength(frame->size());
    server.send(200, "image/jpeg");

    WiFiClient client = server.client();
    frame->writeTo(client);
}


