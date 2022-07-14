import urllib.request, os, cv2
import numpy as np
from time import sleep


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
def run(networkName, urlCamera, urlNode1, urlNode2):
    vermelhos = False
    MAX = 5
    vetor = np.zeros(MAX)
    i = 0

    def conectarRede(networkName):
        os.system(f'''cmd /c "netsh wlan connect name={networkName}"''')

    def requisicao(url):
        try:
            return urllib.request.urlopen(url)
        except Exception:
            return False

    def processaSinal(vermelhos):
        nonlocal vetor, i

        if vermelhos:
            print('SEMÁFORO VERMELHO DETECTADO!')
            vetor[i] = 1
        else:
            print('SEMÁFORO VERMELHO NÃO DETECTADO!')
            vetor[i] = 0

        i = i + 1
        
        if i < MAX:
            return 1
            
        if i == MAX:
            i = 0
            vetor.fill(0)
            
            if np.mean(vetor) > 0.5:
                return 2
            
            if np.mean(vetor) < 0.5:
                return 3

    conectarRede(networkName)
    while True:
        # RECEBENDO AS INFORMAÇÕES CONTIDAS NO ENDEREÇO INDICADO
        WEBinfo = requisicao(urlCamera)

        if not WEBinfo:
            print('Sem Resposta')
            sleep(0.5)
            continue

        try:
            # CONVERTENDO A INFORMAÇÃO PARA UM ARRAY DE BYTES TIPO UINT8
            img = np.array(bytearray(WEBinfo.read()), dtype=np.uint8)
            img = cv2.imdecode(img, -1)
            vermelhos = reconhecerVermelhos(img)
        except Exception:
            print('Erro ao passar imagem para Array!')
            continue

        sinal = processaSinal(vermelhos)

        if sinal == 2:
            requisicao(urlNode1 + 'ATIVAR')
            requisicao(urlNode2 + 'ATIVAR')
        if sinal == 3:
            requisicao(urlNode1 + 'DESATIVAR')
            requisicao(urlNode2 + 'DESATIVAR')

        sleep(0.01)


run('ProjetoSemaforo', 'http://192.168.4.4/cam-hi.jpg', 'http://192.168.4.1/', 'http://192.168.4.3/')