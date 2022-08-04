from code import interact
import urllib.request, os, cv2
import numpy as np
from time import sleep
from time import time


# CRIANDO UMA IMAGEM QUE APRESENTA APENAS O INTERVALO RGB ESCOLHIDO
def juntarIntervalos(HSV):
    intervalos = [
        [[170, 127, 251], [180, 137, 261]],
        [[173, 135, 247], [183, 145, 257]],
        [[170, 168, 255], [180, 178, 265]],
        [[167, 102, 251], [177, 112, 261]],
        [[168, 151, 250], [178, 161, 260]],
        [[14, 129, 241], [24, 139, 251]],
        [[14, 106, 239], [24, 116, 249]],
        [[170, 123, 248], [180, 133, 258]],
        [[164, 139, 255], [174, 149, 265]],
        [[171, 163, 252], [181, 173, 262]],
        [[174, 141, 252], [184, 151, 262]],
        [[165, 168, 85], [175, 178, 95]],
        [[169, 176, 247], [179, 186, 257]],
        [[169, 168, 251], [179, 178, 261]]
    ]
    
    for c in range(len(intervalos)):
        low  = np.array(intervalos[c][0])
        high = np.array(intervalos[c][1])
        intervalos[c] = cv2.inRange(HSV, low, high)

    mask = intervalos[0]
    for c in range(1, len(intervalos)):
        mask = cv2.add(mask, intervalos[c])

    return mask


# RECONHECENDO O CÍRCULO MAIS VERMELHOS PRESENTE EM UMA IMAGEM
def reconhecerVermelhos(img):
    HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    maskr = juntarIntervalos(HSV)

    redCircles = cv2.HoughCircles(maskr, cv2.HOUGH_GRADIENT, 1, minDist=80,
                                     param1=50, param2=10, minRadius=5, maxRadius=300)

    if type(redCircles).__module__ == np.__name__:
        return True

    return False


# NOME DA REDE, URL PRA ATIVAR A CAMERA, URL PARA ATIVAR O COMANDO
def run(networkName, urlCamera, urlNode1, urlNode2):
    MAX = 1                         # TAMANHO DO VETOR DE DETECÇÕES
    vermelhos = False               # VARIÁVEL DE DETECÇÃO DO SINAL
    vetor = np.zeros(MAX)           # VETOR DE DETECÇÕES
    utlimaAtualizacao = time()      # VARIÁVEL PARA SINCRONIZAÇÃO DO SINAL
    i = 0                           # VARIÁVEL PARA PREENCHER VETOR
    x = 0                           # VARIÁVEL PARA DETECTAR PROBLEMAS DE LEITURA

    def conectarRede(networkName):
        os.system(f'''cmd /c "netsh wlan connect name={networkName}"''')

    def requisicao(url, tempoResposta):
        try:
            return urllib.request.urlopen(url, timeout=tempoResposta)
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
        WEBinfo = requisicao(urlCamera + 'cam-hi.jpg', tempoResposta=0.7)

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
            print('ATIVANDO RELÉ')
            requisicao(urlNode1 + 'ATIVAR', tempoResposta=2)
            requisicao(urlNode2 + 'ATIVAR', tempoResposta=2)

        if sinal == 3:
            print('DESATIVANDO RELÉ')
            requisicao(urlNode1 + 'DESATIVAR', tempoResposta=2)
            requisicao(urlNode2 + 'DESATIVAR', tempoResposta=2)

        sleep(0.01)


run('ProjetoSemaforo', 'http://192.168.4.4/', 'http://192.168.4.1/', 'http://192.168.4.3/')