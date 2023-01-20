import cv2
import urllib.request
import numpy as np
import os
from time import sleep
from time import time

urlCamera = 'http://192.168.4.4/cam-hi.jpg'
destino   = 'Teste/'
x = 0

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


def downloadImages(img):
    global x
    x += 1

    cv2.imwrite(destino + rf'teste{x}.png', img)
    print('IMAGEM SALVA')


def main():
    global urlCamera
    print('APERTE "ENTER" PARA BAIXAR A IMAGEM')
    sleep(1)

    while True:
        WEBinfo = requisicao(urlCamera, timeout=5)
        if not WEBinfo:
            print('erro na leitura da camera...')
            continue

        try:
            img = np.array(bytearray(WEBinfo.read()), dtype=np.uint8)
            img = cv2.imdecode(img, -1)
            img = zoom(img, 2)

            cv2.imshow("streaming", img)
            if cv2.waitKey(1) == 13:
                downloadImages(img)
        except:
            print('erro na leitura da câmera...')
            continue
        

conectarRede('ProjetoSemaforo')
#sleep(5)
main()