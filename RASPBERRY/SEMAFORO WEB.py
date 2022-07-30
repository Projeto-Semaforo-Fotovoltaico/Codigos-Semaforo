import urllib.request, os, cv2
import numpy as np
from time import sleep
from time import time


# RECONHECENDO O CÍRCULO MAIS VERMELHOS PRESENTE EM UMA IMAGEM
def reconhecerVermelhos(img):
    HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    low1 = np.array([14, 129, 241])
    high1 = np.array([24, 139, 251])

    low2 = np.array([14, 106, 239])
    high2 = np.array([24, 116, 249])

    mask1 = cv2.inRange(HSV, low1, high1)
    mask2 = cv2.inRange(HSV, low2, high2)
    
    maskr = cv2.add(mask1, mask2)

    redCircles = cv2.HoughCircles(maskr, cv2.HOUGH_GRADIENT, 1, minDist=80,
                                     param1=50, param2=9.9, minRadius=5, maxRadius=300)

    if type(redCircles).__module__ == np.__name__:
        return True

    return False


# NOME DA REDE, URL PRA ATIVAR A CAMERA, URL PARA ATIVAR O COMANDO
def run(networkName, urlCamera, urlNode1, urlNode2):
    MAX = 5
    vermelhos = False
    vetor = np.zeros(MAX)
    utlimaAtualizacao = time()
    i = 0
    x = 0

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
            
            if np.mean(vetor) > 0.5:
                vetor.fill(0)
                return 2
            
            if np.mean(vetor) < 0.5:
                vetor.fill(0)
                return 3


    conectarRede(networkName)
    while True:
        # RECEBENDO AS INFORMAÇÕES CONTIDAS NO ENDEREÇO INDICADO
        WEBinfo = requisicao(urlCamera + 'cam-hi.jpg')

        if x == 10:
            print('Resetando ESP')
            requisicao(urlCamera + 'RESET')
            x = 0
            sleep(10)

        if not WEBinfo:
            print('Sem Resposta')
            sleep(0.5)
            x = x + 1
            continue

        try:
            # CONVERTENDO A INFORMAÇÃO PARA UM ARRAY DE BYTES TIPO UINT8
            tempo = time()
            img = np.array(bytearray(WEBinfo.read()), dtype=np.uint8)
            print('TEMPO PARA LEITURA: ', time() - tempo, '\n')

            img = cv2.imdecode(img, -1)
            vermelhos = reconhecerVermelhos(img)
        except Exception:
            print('Erro ao passar imagem para Array!')
            x = x + 1
            continue

        sinal = processaSinal(vermelhos)

        if sinal == 2:
            print('ATIVANDO RELÉ')
            requisicao(urlNode1 + 'ATIVAR')
            requisicao(urlNode2 + 'ATIVAR')

            utlimaAtualizacao = utlimaAtualizacao - time()
            print('ATUALIZAÇÃO VERMELHO: ')
        if sinal == 3:
            print('DESATIVANDO RELÉ')
            requisicao(urlNode1 + 'DESATIVAR')
            requisicao(urlNode2 + 'DESATIVAR')

        sleep(0.01)


run('ProjetoSemaforo', 'http://192.168.4.4/', 'http://192.168.4.1/', 'http://192.168.4.3/')