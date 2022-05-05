import urllib.request, os, cv2
import numpy as np
from time import sleep
from time import time

i = 0
tempoI = time()

# MOSTRANDO A IMAGEM PELO SEU OBJETO E ESPERANDO
def show(img):
    img = cv2.resize(img, (800, 600), interpolation=cv2.INTER_CUBIC)
    cv2.imshow('imagem', img)
    cv2.waitKey(0)


# DESENHANDO OS CÍRCULOS EM UMA LISTA DE COORDENADAS
def desenharCirculos(img, detected):
    if not len(detected):
        return

    x, y, r = int(detected[0]), int(detected[1]), int(detected[2])

    img = cv2.circle(img, (x, y), r, (0, 255, 0), 2)

    img = cv2.rectangle(img, (x - 3 * r, y - 3 * r),
                             (x + 3 * r, y + 3 * r),
                             (0, 0, 255), thickness=4)
    return img


# RECONHECENDO O CÍRCULO MAIS VERMELHOS PRESENTE EM UMA IMAGEM
def reconhecerVermelhos(img):
    HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    low = np.array([170, 150, 100])
    high = np.array([180, 220, 190])
    maskr = cv2.inRange(HSV, low, high)

    redCircles = cv2.HoughCircles(maskr, cv2.HOUGH_GRADIENT, 1, minDist=80,
                                     param1=50, param2=10, minRadius=5, maxRadius=300)

    if type(redCircles).__module__ == np.__name__:
        return True

    return False


# NOME DA REDE, URL PRA ATIVAR A CAMERA, URL PARA ATIVAR O COMANDO
def run(networkName, url, comando):
    def conectarRede(networkName):
        os.system(f'''cmd /c "netsh wlan connect name={networkName}"''')

    def requisicao(url):
        try:
            return urllib.request.urlopen(url)
        except Exception:
            return False

    conectarRede(networkName)
    while True:
        # RECEBENDO AS INFORMAÇÕES CONTIDAS NO ENDEREÇO INDICADO
        WEBinfo = requisicao(url)
        if not WEBinfo:
            continue

        # CONVERTENDO A INFORMAÇÃO PARA UM ARRAY DE BYTES TIPO UINT8
        img = np.array(bytearray(WEBinfo.read()), dtype=np.uint8)
        img = cv2.imdecode(img, -1)
        vermelhos = reconhecerVermelhos(img)

        if vermelhos:
            print('SEMÁFORO VERMELHO DETECTADO!')
            requisicao(comando + 'ATIVAR')
        else:
            print('SEMÁFORO VERMELHO NÃO DETECTADO!')
            requisicao(comando + 'DESATIVAR')


run('ProjetoSemaforo', 'http://192.168.4.3/cam-hi.jpg', 'http://192.168.4.1/')