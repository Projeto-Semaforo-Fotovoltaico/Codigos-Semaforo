from tkinter.tix import MAX
import urllib.request, os, cv2
import numpy as np
from time import sleep, time


# VARIÁVEIS GLOBAIS PARA SEREM UTILIZADAS NAS FUNÇÕES DO ALGORÍTIMO
temposVermelho = []     # VETOR PARA ARMAZENAR OS TEMPOS DE DECÇÕES VERMELHO
temposResto    = []     # VETOR PARA ARMAZENAR OS TEMPOS DE DECÇÕES NÃO VERMELHO
sinc = 0                # VARIÁVEL PARA CONTAGEM DE DETECÇÕES
atualizacao = time()    # VARIÁVEL ARMAZENAR O TEMPO DA ÚLTIMA ATUALIZAÇÃO
vermelhos = False       # VARIÁVEL DE DETECÇÃO DO SINAL
estadoAnterior = False  # VARIÁVEL PARA ARMAZENAR O ESTADO ANTERIOR
MAX = 10


# VARIÁVEIS GLOBAIS PARA LINKS DE REQUISIÇÃO WEB SERVIDOR LOCAL
networkName = 'ProjetoSemaforo'
urlCamera   = 'http://192.168.4.4/'
urlNode1    = 'http://192.168.4.1/'
urlNode2    = 'http://192.168.4.3/'


# ENVIAR UMA REQUISIÇÃO PARA UM LINK COM UM TEMPO MÁXIMO DE RESPOSTA
def requisicao(url, timeout):
    try:
        return urllib.request.urlopen(url, timeout=timeout)
    except Exception:
        return False


# CONECTANDO A UMA REDE WIFI PELO PC ATRAVÉS DE SEU NOME PÚBLICO
def conectarRede(networkName):
    os.system(f'''cmd /c "netsh wlan connect name={networkName}"''')


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
        [[174, 132, 245], [184, 142, 255]],
        [[171, 145, 254], [181, 155, 264]],
        [[175, 169, 245], [185, 179, 255]],
        [[168, 172, 253], [178, 182, 263]],
        [[172, 189, 251], [182, 199, 261]],
        [[170, 158, 255], [180, 168, 265]],
        [[165, 139, 74], [175, 149, 84]],
        [[174, 171, 247], [184, 181, 257]],
        [[172, 207, 128], [182, 217, 138]],
        [[170, 210, 128], [180, 220, 138]],
        [[169, 212, 81], [179, 222, 91]],
        [[170, 214, 249], [180, 224, 259]],
        [[175, 233, 198], [185, 243, 208]],
        [[175, 236, 179], [185, 246, 189]]
    ]
    
    for c in range(len(intervalos)):
        low  = np.array(intervalos[c][0])
        high = np.array(intervalos[c][1])
        intervalos[c] = cv2.inRange(HSV, low, high)

    mask = intervalos[0]
    for c in range(1, len(intervalos)):
        mask = cv2.add(mask, intervalos[c])

    return mask


# RETORNANDO O ESTADO DE DETECÇÃO ENCONTRADO PARA PREENCHER O VETOR
def processaSinal(vermelhos):
    global vetor, i

    if vermelhos:
        print('SEMÁFORO VERMELHO DETECTADO!')
        return True
    
    print('SEMÁFORO VERMELHO NÃO DETECTADO!')
    return False


# SE O SINAL MUDOU PARA VERMELHO, ARMAZENE O TEMPO DE SINAL NÃO VERMELHO (VICE-VERSA)
def adicionarSinal(sinal):
    global temposVermelho, temposResto, sinc, atualizacao, estadoAnterior
    tempo = time()

    if sinal:
        requisicao(urlNode2 + 'ATIVAR', timeout=0.2) # SINAL VERMELHO
        requisicao(urlNode1 + 'ATIVAR', timeout=0.2) # SINAL VERMELHO

        print(f'{atualizacao} ADICIONADO AO SINAL NÃO VERMELHO')
        temposResto.append(atualizacao)
    else:
        requisicao(urlNode2 + 'DESATIVAR', timeout=0.2) # SINAL NÃO VERMELHO
        requisicao(urlNode1 + 'DESATIVAR', timeout=0.2) # SINAL NÃO VERMELHO

        print(f'{atualizacao} ADICIONADO AO SINAL VERMELHO')
        temposVermelho.append(atualizacao)

    sinc = sinc + 1          # INCREMENTANDO A SINCRONIZAÇÃO
    estadoAnterior = sinal   # ATUALIZANDO O ESTADO ANTERIOR
    atualizacao = time()     # ATUALIZANDO O TEMPO DE ATUALIZAÇÃO


# RETORNANDO A MÉDIA DE UMA LISTA SEM OUTLIERS
def treatData(list):
    array = np.array(list)
    
    std  = np.std(array)
    mean = np.mean(array)

    upper = mean + 1*std
    lower = mean - 1*std

    array = array[(array > lower) & (array < upper)]
    return np.mean(array)


# ADICIONANDO OS TEMPOS EM QUE O SINAL VERMELHO FICOU DESATIVADO
def verificarSincronismo(sinal):
    global atualizacao, sinc, temposVermelho, temposResto
    global estadoAnterior, urlNode1, urlNode2

    # PRIMERIA VEZ QUE ENTRA NA FUNÇÃO, ESTABELEÇA AS CONDIÇÕES INICIAIS
    if sinc == 0:
        adicionarSinal(sinal)
        return False

    # SÓ PROSSEGUE SE O SINAL MUDAR DE ESTADO E DEMORAR MAIS QUE 7 SEGUNDOS (GARANTIA)
    if estadoAnterior == sinal or time() - atualizacao < 7:
        return False

    # ENCONTRANDO E ATUALIZANDO O TEMPO DE VARIAÇÃO DE SINAL
    atualizacao = time() - atualizacao
    
    # TOTAL DE VARIAÇÕES DE SINAL NECESSÁRIAS PARA SINCRONIZAÇÃO
    if sinc == MAX:
        mediaVermelhos = int(treatData(temposVermelho[2:]) * 1000)
        mediaResto     = int(treatData(temposResto[2:])    * 1000)
        sinal = int(sinal)

        print(f'MÉDIA DOS TEMPOS DE SINAIS VERMELHOS:     {mediaVermelhos/1000}')
        print(f'MÉDIA DOS TEMPOS DE SINAIS NÃO VERMELHOS: {mediaResto/1000}')
        print(f'ATIVANDO ESTADO {sinal}')
        
        requisicao(urlNode2 + f'SINC?{mediaVermelhos}|{mediaResto}|{sinal}|', timeout=0.2)
        requisicao(urlNode1 + f'SINC?{mediaVermelhos}|{mediaResto}|{sinal}|', timeout=0.2)
        return True
    
    # A CADA VARIAÇÃO DE SINAL, INCREMENTE A VARIÁVEL E RESETE A CONTAGEM
    adicionarSinal(sinal)
    return False


# FUNÇÃO PRINCIPAL DO PROGRAMA NO MODO LOOP ATÉ O SINCRONISMO
def main():
    global networkName, vermelhos, urlCamera
    conectarRede(networkName)
    sleep(5)

    while True:
        # RECEBENDO AS INFORMAÇÕES CONTIDAS NO ENDEREÇO INDICADO
        WEBinfo = requisicao(urlCamera + 'cam-hi.jpg', timeout=2)

        if not WEBinfo:
            print('Sem Resposta')
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
        if verificarSincronismo(sinal):
            break

main()