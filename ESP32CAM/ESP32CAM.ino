#include "esp_camera.h"
#include <WiFi.h>

#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

WiFiServer server(80);


// CONECTANDO À REDE LOCAL PELO NOME E SENHA
void conectarRede(char* nomeRede, char* senhaRede){
    WiFi.mode(WIFI_STA);
    WiFi.begin(nomeRede, senhaRede);

    // (OPCIONAL) CONFIGURAÇÕES SECUNDÁRIAS DO SERVIDOR LOCAL
    IPAddress staticIP(192, 168, 4, 6);      // IP ESTÁTICO (REQUISIÇÕES)
    IPAddress gateway(192, 168, 4, 12);      // GATEWAY ESTÁTICO IP
    IPAddress subnet(255, 255, 255, 0);      // OCULTAR SUB REDE
    WiFi.config(staticIP, gateway, subnet);

    while(WiFi.status() != WL_CONNECTED){
        delay(500);
        Serial.print(F("."));
    }

    server.begin();
}


// EXIBINDO INFORMAÇÕES DA REDE CONECTADA
void exibirInformacoes(){
    Serial.print(F("\n"));
    
    if (WiFi.status() == WL_CONNECTED)
        Serial.print(F("WIFI CONECTADO!\n"));
    else
        Serial.print(F("WIFI NÃO CONECTADO!\n"));
  
    Serial.print(F("ENDERECOIP: "));
    Serial.print(WiFi.localIP());
    Serial.print(F("\n"));
}


void configurarCamera(){
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
    config.frame_size = FRAMESIZE_VGA;
    config.pixel_format = PIXFORMAT_JPEG; 
    config.grab_mode = CAMERA_GRAB_LATEST;
    config.fb_location = CAMERA_FB_IN_PSRAM;
    config.jpeg_quality = 3;
    config.fb_count = 2;

    // INICIALIZANDO A CAMERA
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK){
        Serial.println("ERRO AO INICIALIZAR A CÂMERA"); 
        ESP.restart();
    }

    Serial.println("CÂMERA PRONTA");
}


void sendImage(WiFiClient &client){
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Erro ao capturar a imagem");
        return;
    }
    
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: image/jpeg");
    client.print("Content-Length: ");
    client.println(fb->len);
    client.println("Connection: close");
    client.println();

    client.write(fb->buf, fb->len);
    esp_camera_fb_return(fb);
}


void reconectarRede(void){
    if(WiFi.status() == WL_CONNECTED)
        return;

    Serial.println("Reconnecting to WiFi...");
    ESP.restart();
}


void setup(){
    Serial.begin(9600); 
    Serial.setDebugOutput(false);
    conectarRede("ProjetoSemaforo", "12345678");

    exibirInformacoes();
    configurarCamera();

    ledcSetup(0, 5000, 8);  // PINO PWM DE FREQUÊNCIA 500 HZ
    ledcAttachPin(4, 0);    // ADICIONANDO O LED AO CANAL 0
    ledcWrite(0, 1);        // BRILHO 1 DE 255
}


void loop(){
    reconectarRede();

    WiFiClient client = server.available();
    client.setTimeout(5000);
  
    // ENQUANTO NÃO FOR CONECTADO NO SERVIDOR CLIENTE
    if (!client)
        return;

    // SE O SERVIDOR CLIENTE NÃO ESTIVER DISPONÍVEL
    if(!client.available())
        return;

    String requisicao = client.readStringUntil('\r'); 
    if(requisicao.indexOf("/CAPTURE") != -1)
        sendImage(client);

    client.flush();
    client.stop();
    delay(1);
}
