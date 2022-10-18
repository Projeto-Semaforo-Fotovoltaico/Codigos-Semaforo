#include "esp_camera.h"
#include <WiFi.h>

#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

WiFiServer server(80);
void paginaHTML(WiFiClient *cl);

const char* ssid = "ProjetoSemaforo";
const char* password = "12345678";

void configurarCamera(void);
void startCameraServer();
void conectarRede();
void exibirInformacoes();


void setup() {
    Serial.begin(9600);
  
    configurarCamera();
    conectarRede();
    startCameraServer();
    exibirInformacoes();
}


void conectarRede(){
    WiFi.begin(ssid, password);
    WiFi.setSleep(false);
    
    IPAddress staticIP(192, 168, 4, 4); // REQUISIÇÃO
    IPAddress gateway(192, 168, 4, 5);     
    IPAddress subnet(255, 255, 255, 0);   
    WiFi.config(staticIP, gateway, subnet);
  
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    Serial.println("");
    Serial.println("WiFi connected");
    server.begin();
}


void exibirInformacoes(){
    Serial.print("CAMERA PRONTA, SERVIDOR EM: http://");
    Serial.print(WiFi.localIP());
}


// CASO DESCONECTE COM A REDE, RESETAR O ESP
void reconectarRede(void){
    if ((WiFi.status() != WL_CONNECTED)){
        delay(10000);
        Serial.println("SEM CONEXÃO.... RESETANDO ESP");
        ESP.restart();
    }
}


void loop() {
    reconectarRede();
    WiFiClient client = server.available();
    
    // LOOP INFINITO ENQUANTO O SERVIDOR CLIENTE NÃO FOR CONECTADO
    if (!client)
      return;
    
    String requisicao = client.readStringUntil('\r');
    Serial.print("REQUISICAO: ");
    Serial.println(requisicao);
    
    if(requisicao.indexOf("/RESET") != -1){
      Serial.println("RESETANDO O ESP!");
      ESP.restart();
    }
  
    // SE FOR CHAMADO A PÁGINA DE MENU PRINCIPAL
    if(requisicao.indexOf("/MENU") != -1)
      paginaHTML(&client);
    
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


// FUNÇÕES PRINCIPAIS PARA CONFIGURARA A CÂMERA
void configurarCamera(void){
    Serial.setDebugOutput(true);
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.frame_size = FRAMESIZE_UXGA;
    config.pixel_format = PIXFORMAT_JPEG; 
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
    config.fb_location = CAMERA_FB_IN_PSRAM;
    config.jpeg_quality = 12;
    config.fb_count = 1;
    
    if(config.pixel_format == PIXFORMAT_JPEG){
      if(psramFound()){
        config.jpeg_quality = 10;
        config.fb_count = 2;
        config.grab_mode = CAMERA_GRAB_LATEST;
      } else {
        // Limit the frame size when PSRAM is not available
        config.frame_size = FRAMESIZE_SVGA;
        config.fb_location = CAMERA_FB_IN_DRAM;
      }
    } else {
      // Best option for face detection/recognition
      config.frame_size = FRAMESIZE_240X240;
      #if CONFIG_IDF_TARGET_ESP32S3
          config.fb_count = 2;
      #endif
     }
    
    #if defined(CAMERA_MODEL_ESP_EYE)
      pinMode(13, INPUT_PULLUP);
      pinMode(14, INPUT_PULLUP);
    #endif
  
    // camera init
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
      Serial.printf("Camera init failed with error 0x%x", err);
      delay(500);
      ESP.restart();
    }
  
    sensor_t * s = esp_camera_sensor_get();
    // initial sensors are flipped vertically and colors are a bit saturated
    if (s->id.PID == OV3660_PID) {
      s->set_vflip(s, 1); // flip it back
      s->set_brightness(s, 1); // up the brightness just a bit
      s->set_saturation(s, -2); // lower the saturation
    }
    // drop down frame size for higher initial frame rate
    if(config.pixel_format == PIXFORMAT_JPEG){
      s->set_framesize(s, FRAMESIZE_QVGA);
    }
    
    #if defined(CAMERA_MODEL_M5STACK_WIDE) || defined(CAMERA_MODEL_M5STACK_ESP32CAM)
      s->set_vflip(s, 1);
      s->set_hmirror(s, 1);
    #endif
    
    #if defined(CAMERA_MODEL_ESP32S3_EYE)
      s->set_vflip(s, 1);
    #endif
}
