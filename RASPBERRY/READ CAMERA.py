import cv2
import urllib.request
import numpy as np
import os
from time import sleep
from time import time

urlCamera = 'http://192.168.4.4'


def conectarRede(networkName):
    os.system(f'''cmd /c "netsh wlan connect name={networkName}"''')


def requisicao(url, timeout):
    try:
        return urllib.request.urlopen(url, timeout=timeout)
    except Exception:
        return False


def zoom(img, zoom_factor=1.5):
    y_size = img.shape[0]
    x_size = img.shape[1]

    x1 = int(0.5*x_size*(1-1/zoom_factor))
    x2 = int(x_size-0.5*x_size*(1-1/zoom_factor))
    y1 = int(0.5*y_size*(1-1/zoom_factor))
    y2 = int(y_size-0.5*y_size*(1-1/zoom_factor))

    img_cropped = img[y1:y2,x1:x2]
    return cv2.resize(img_cropped, None, fx=zoom_factor, fy=zoom_factor)


def main():
    global urlCamera
    
    if not requisicao(urlCamera + ":81/stream", timeout=10):
        print('Câmera não está funcionando... Resetando ESP32')
        requisicao(urlCamera + r'\RESET', timeout=5)
        sleep(5)
        return main()

    requisicao(urlCamera + "/control?var=quality&val=10", timeout=5)
    requisicao(urlCamera + "/control?var=framesize&val=9", timeout=5)

    sleep(1)
    cap = cv2.VideoCapture(urlCamera + ":81/stream")

    while True:
        erro = time()
        if not cap.isOpened():
            print('Erro na leitura da câmera...')
            sleep(0.5)
            continue
        
        try:
            ret, img = cap.read()
            img = zoom(img, 2)
            erro = time() - erro

            print(f'erro: {erro:.5f}')
            cv2.imshow("streaming", img)
            cv2.waitKey(1)
        except:
            print('erro na leitura da câmera...')
            return main()
        

conectarRede('ProjetoSemaforo')
sleep(5)
main()