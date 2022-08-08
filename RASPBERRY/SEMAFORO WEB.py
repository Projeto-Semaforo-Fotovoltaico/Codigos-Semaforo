import urllib.request, os, cv2
import numpy as np
from time import sleep, time


# VARIÁVEIS GLOBAIS PARA SEREM UTILIZADAS NAS FUNÇÕES DO ALGORÍTIMO
i = 0                   # VARIÁVEL PARA PREENCHER VETOR
MAX = 1                 # TAMANHO DO VETOR DE DETECÇÕES
vermelhos = False       # VARIÁVEL DE DETECÇÃO DO SINAL
vetor = np.zeros(MAX)   # VETOR DE DETECÇÕES
sinc = 0                # VARIÁVEL PARA CONTAGEM DE DETECÇÕES
temposVermelho = []     # VETOR PARA ARMAZENAR OS TEMPOS DE DECÇÕES VERMELHO
temposResto    = []     # VETOR PARA ARMAZENAR OS TEMPOS DE DECÇÕES NÃO VERMELHO
atualizacao = time()    # VARIÁVEL PARA TEMPO DE SINAL VERMELHO


# RECONHECENDO O CÍRCULO MAIS VERMELHOS PRESENTE EM UMA IMAGEM
def reconhecerVermelhos(img):
    HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    maskr = juntarIntervalos(HSV)

    redCircles = cv2.HoughCircles(maskr, cv2.HOUGH_GRADIENT, 1, minDist=80,
                                    param1=50, param2=10, minRadius=5, maxRadius=300)

    if type(redCircles).__module__ == np.__name__:
        return True

    return False


# CRIANDO UMA IMAGEM QUE APRESENTA APENAS O INTERVALO RGB ESCOLHIDO
def juntarIntervalos(HSV):
    intervalos = [
        [[170, 127, 251], [180, 137, 261]],
        [[173, 135, 247], [183, 145, 257]],
        [[170, 168, 255], [180, 178, 265]],
        [[167, 102, 251], [177, 112, 261]],
        [[168, 151, 250], [178, 161, 260]],
        [[14, 129, 241],  [24, 139, 251] ],
        [[14, 106, 239],  [24, 116, 249] ],
        [[170, 123, 248], [180, 133, 258]],
        [[164, 139, 255], [174, 149, 265]],
        [[171, 163, 252], [181, 173, 262]],
        [[174, 141, 252], [184, 151, 262]],
        [[165, 168, 85],  [175, 178, 95] ],
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


# ADICIONANDO OS TEMPOS EM QUE O SINAL VERMELHO FICOU DESATIVADO
def verificarSincronismo(sinal):
    global atualizacao, sinc, temposVermelho, temposResto
    atualizacao = time() - atualizacao
    
    if sinc == 20:
        mediaVermelhos = np.mean(temposVermelho[1:])
        mediaResto     = np.mean(temposResto[1:])

        print(f'MÉDIA DOS TEMPOS DE SINAIS VERMELHOS: {mediaVermelhos}')
        print(f'MÉDIA DOS TEMPOS DE SINAIS VERMELHOS: {mediaResto}')
        return

    if sinal == 2 and atualizacao > 5:
        print(f'{atualizacao} ADICIONADO AO SINAL VERMELHO')
        temposVermelho.append(atualizacao)

    if sinal == 3 and atualizacao > 5:
        print(f'{atualizacao} ADICIONADO AO SINAL NÃO VERMELHO')
        temposResto.append(atualizacao)

    if sinal == 2 or sinal == 3:
        sinc = sinc + 1
        atualizacao = time()


# RETORNANDO O ESTADO DE DETECÇÃO ENCONTRADO PARA PREENCHER O VETOR
def processaSinal(vermelhos):
    global vetor, i

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


def requisicao(url, timeout):
    try:
        return urllib.request.urlopen(url, timeout=timeout)
    except Exception:
        return False


def conectarRede(networkName):
    os.system(f'''cmd /c "netsh wlan connect name={networkName}"''')


# NOME DA REDE, URL PRA ATIVAR A CAMERA, URL PARA ATIVAR O COMANDO
def main(networkName, urlCamera, urlNode1, urlNode2):
    global vermelhos, vetor, i, MAX
    conectarRede(networkName)

    while True:
        # RECEBENDO AS INFORMAÇÕES CONTIDAS NO ENDEREÇO INDICADO
        WEBinfo = requisicao(urlCamera + 'cam-hi.jpg', timeout=0.7)

        if not WEBinfo:
            print('Sem Resposta')
            print()
            sleep(0.3)
            continue

        try:
            # CONVERTENDO A INFORMAÇÃO PARA UM ARRAY DE BYTES TIPO UINT8
            img = np.array(bytearray(WEBinfo.read()), dtype=np.uint8)
            img = cv2.imdecode(img, -1)
            
            vermelhos = reconhecerVermelhos(img)

        except Exception:
            print('Erro ao passar imagem para Array!')
            print()
            continue

        sinal = processaSinal(vermelhos)
        if sinal == 1:
            continue
        
        verificarSincronismo(sinal)

        if sinal == 2:
            print('ATIVANDO RELÉ')
            requisicao(urlNode1 + 'ATIVAR', timeout=1)
            requisicao(urlNode2 + 'ATIVAR', timeout=1)

        if sinal == 3:
            print('DESATIVANDO RELÉ')
            requisicao(urlNode1 + 'DESATIVAR', timeout=1)
            requisicao(urlNode2 + 'DESATIVAR', timeout=1)

        print()
        sleep(0.1)


main('ProjetoSemaforo', 'http://192.168.4.4/', 'http://192.168.4.1/', 'http://192.168.4.3/')