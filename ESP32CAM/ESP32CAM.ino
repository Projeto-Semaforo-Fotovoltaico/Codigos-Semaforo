#include "esp_camera.h"
#include <WiFi.h>

#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"
#define LED 16

WiFiServer server(80);
void paginaHTML(WiFiClient *cl);



void configurarCamera(void);
void startCameraServer();
void setupLedFlash(int pin);
void conectarRede(void);
void exibirInformacoes(void);


void conectarRede(){
    WiFi.begin(ssid, password);
    
    IPAddress staticIP(192, 168, 4, 4); // REQUISIÇÃO
    IPAddress gateway(192, 168, 4, 12);     
    IPAddress subnet(255, 255, 255, 0);   
    WiFi.config(staticIP, gateway, subnet);
  
    while (WiFi.status() != WL_CONNECTED){
      Serial.print(".");
      delay(1000);
    }
    Serial.println("");
    Serial.println("WiFi connected");
    server.begin();
}


void exibirInformacoes(){
    Serial.print("CAMERA PRONTA, SERVIDOR EM: http://");
    Serial.print(WiFi.localIP());
    Serial.println();
    digitalWrite(LED, HIGH);
}


// CASO DESCONECTE COM A REDE, RESETAR O ESP
void reconectarRede(void){
    if ((WiFi.status() != WL_CONNECTED)){
        Serial.println("SEM CONEXÃO.... RESETANDO ESP");
        delay(5000);
        setup();
    }
}


void setup() {
    Serial.begin(9600);
    
    pinMode(LED, OUTPUT);
    digitalWrite(LED, HIGH);
  
    configurarCamera();
    conectarRede();
    startCameraServer();
    exibirInformacoes();
}


void loop() {
    reconectarRede();
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
