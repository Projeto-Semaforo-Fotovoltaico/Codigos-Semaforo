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


# INICIANDO E CONECTANDO COM O SERVIDOR DA CÂMERA 
def initCamera():
    global urlCamera

    if not requisicao(urlCamera + ":81/stream", timeout=10):
        sleep(0.5)
        return None

    requisicao(urlCamera + "/control?var=quality&val=10", timeout=5)
    requisicao(urlCamera + "/control?var=framesize&val=9", timeout=5)

    sleep(1)
    return cv2.VideoCapture(urlCamera + ":81/stream")


# OBTENDO E ARMAZENANDO O ATUAL QUADRO DA FILMAGEM 
def getImage(cap):
    if cap is None or not cap.isOpened():
        return None
    
    try:
        ret, img = cap.read()
        img = zoom(img, 2)
        return img
    except:
        return None


def main():
    global urlCamera
    sleep(1)

    cap = initCamera()

    while True:
        img = getImage(cap)

        if img is None:
            print('CÂMERA NÃO FUNCIONANDO')
            sleep(0.5)
            return main()

        cv2.imshow("streaming", img)
        cv2.waitKey(1)            


conectarRede('ProjetoSemaforo')
main()