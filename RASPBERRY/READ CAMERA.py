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


def main():
    global urlCamera

    if not requisicao(urlCamera + ":81/stream", timeout=10):
        print('Câmera não está funcionando... Resetando ESP32')
        requisicao(urlCamera + r'\RESET', timeout=2)
        sleep(5)
        return main()

    requisicao(urlCamera + "/control?var=quality&val=30", timeout=5)
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
            erro = time() - erro

            print(f'erro: {erro:.5f}')
            cv2.imshow("streaming", img)
            cv2.waitKey(1)
        except:
            print('erro na leitura da câmera...')
            return main()
        

conectarRede('ProjetoSemaforo')
main()