import cv2
import urllib.request
import numpy as np
import os
from time import sleep
from time import time

urlCamera = r'http://192.168.4.6/CAPTURE'


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


# OBTENDO E ARMAZENANDO O ATUAL QUADRO DA FILMAGEM 
def getImage(url):
    try:
        img = urllib.request.urlopen(url, timeout=6)
        img = np.array(bytearray(img.read()), dtype=np.uint8)
    except:
        return None
    
    return cv2.imdecode(img, -1)


def main():
    global urlCamera

    while True:
        img = getImage(urlCamera)

        if img is None:
            print('CÂMERA NÃO FUNCIONANDO')
            sleep(0.5)
            return main()

        img = zoom(img)
        cv2.imshow("streaming", img)
        cv2.waitKey(1)            

conectarRede('ProjetoSemaforo')
main()