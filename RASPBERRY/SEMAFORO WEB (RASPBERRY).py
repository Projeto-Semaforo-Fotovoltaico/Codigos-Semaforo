import requests, os, cv2
import numpy as np
from time import sleep, time
from RPi.GPIO import *


# VARIÁVEIS GLOBAIS PARA SEREM UTILIZADAS NAS FUNÇÕES DO ALGORÍTIMO
temposVermelho = []     # VETOR PARA ARMAZENAR OS TEMPOS DE DECÇÕES VERMELHO
temposResto    = []     # VETOR PARA ARMAZENAR OS TEMPOS DE DECÇÕES NÃO VERMELHO
sinc = 0                # VARIÁVEL PARA CONTAGEM DE DETECÇÕES 
atualizacao = time()    # VARIÁVEL ARMAZENAR O TEMPO DA ÚLTIMA ATUALIZAÇÃO
vermelhos = False       # VARIÁVEL DE DETECÇÃO DO SINAL
estadoAnterior = False  # VARIÁVEL PARA ARMAZENAR O ESTADO ANTERIOR
erroLeitura = 0         # VARIÁVEL PARA ARMAZENAR O ERRO (TEMPO PARA LEITURA)
MAX = 30                # VARIÁVEL PARA TAMANHO MÁXIMO DO VETOR

# CONFIGURANDO OS PINOS DIGITAIS DO LED DO RASPBERRY
LED = 12
estadoLED = True

cleanup()
setmode(BOARD)
setup(LED, OUT)
output(LED, HIGH)

# VARIÁVEIS GLOBAIS PARA LINKS DE REQUISIÇÃO WEB SERVIDOR LOCAL
urlCamera   = 'http://192.168.4.4/cam-hi.jpg'
#urlCamera   = 'http://pyimagesearch.com/wp-content/uploads/2015/01/opencv_logo.png'
urlNode1    = 'http://192.168.4.1/'
urlNode2    = 'http://192.168.4.3/'

# DADOS QUE SÃO OS INTERVALOS DE DETECÇÃO RGB
dadosRGB = np.array([
    [[169, 158, 248], [179, 168, 258]],
    [[170, 143, 254], [180, 153, 264]],
    [[165, 116, 250], [175, 126, 260]],
    [[174, 139, 249], [184, 149, 259]],
    [[173, 131, 253], [183, 141, 263]],
    [[167, 105, 254], [177, 115, 264]],
    [[170, 147, 255], [180, 157, 265]],
    [[167, 97, 245],  [177, 107, 255]],
    [[172, 187, 253], [182, 197, 263]],
    [[173, 135, 255], [183, 145, 265]],
    [[172, 95, 248],  [182, 105, 258]]
])


# CRIANDO UMA IMAGEM QUE APRESENTA APENAS O INTERVALO RGB ESCOLHIDO
def juntarIntervalos(HSV):
    global dadosRGB
    
    mask = 0
    for c in range(len(dadosRGB)):
        low, high  = dadosRGB[c]
        mask = cv2.add(mask, cv2.inRange(HSV, low, high))
    
    return mask


# DANDO UM ZOOM NA IMAGEM PARA MELHOR DETECÇÃO
def zoom(img, zoom_factor=1.5):
    y_size = img.shape[0]
    x_size = img.shape[1]

    x1 = int(0.5*x_size*(1-1/zoom_factor))
    x2 = int(x_size-0.5*x_size*(1-1/zoom_factor))
    y1 = int(0.5*y_size*(1-1/zoom_factor))
    y2 = int(y_size-0.5*y_size*(1-1/zoom_factor))

    img_cropped = img[y1:y2,x1:x2]
    return cv2.resize(img_cropped, None, fx=zoom_factor, fy=zoom_factor)


# VERIFICANDO SE EXISTE ALGUM CÍRCULO VERMELHO NA IMAGEM
def reconhecerVermelhos(img):
    HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    maskr = juntarIntervalos(HSV)

    redCircles = cv2.HoughCircles(maskr, cv2.HOUGH_GRADIENT, 1, minDist=80,
                                    param1=50, param2=10, minRadius=5, maxRadius=300)

    if type(redCircles).__module__ == np.__name__:
        return True

    return False


# RETORNANDO O ESTADO DE DETECÇÃO ENCONTRADO PARA PREENCHER O VETOR
def processaSinal(vermelhos):
    mudaLED()

    if vermelhos:
        print('SEMÁFORO VERMELHO DETECTADO!')
        return True
    
    print('SEMÁFORO VERMELHO NÃO DETECTADO!')
    return False


# SE O SINAL MUDOU PARA VERMELHO, ARMAZENE O TEMPO DE SINAL NÃO VERMELHO (VICE-VERSA)
def adicionarSinal(sinal):
    global temposVermelho, temposResto, sinc, atualizacao, estadoAnterior

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


# ADICIONANDO OS TEMPOS EM QUE O SINAL VERMELHO FICOU DESATIVADO
def verificarSincronismo(sinal):
    global atualizacao, sinc, temposVermelho, temposResto
    global estadoAnterior, urlNode1, urlNode2, erroLeitura

    # PRIMERIA VEZ QUE ENTRA NA FUNÇÃO, ESTABELEÇA AS CONDIÇÕES INICIAIS
    if sinc == 0:
        adicionarSinal(sinal)
        return False

    # SÓ PROSSEGUE SE O SINAL MUDAR DE ESTADO (ATUALIZAÇÃO DE SINAL)
    if estadoAnterior == sinal:
        return False
    
    # ENCONTRANDO E ATUALIZANDO O TEMPO DE VARIAÇÃO DE SINAL
    atualizacao = time() - atualizacao
    
    # TOTAL DE VARIAÇÕES DE SINAL NECESSÁRIAS PARA SINCRONIZAÇÃO
    if sinc >= MAX and sinal:
        erroTotal      = int((erroLeitura) * 1000)
        mediaVermelhos = int(treatData(temposVermelho[2:])  * 1000)
        mediaResto     = int(treatData(temposResto[2:])     * 1000)

        print(f'MÉDIA DOS TEMPOS DE SINAIS VERMELHOS:         {mediaVermelhos/1000}')
        print(f'MÉDIA DOS TEMPOS DE SINAIS NÃO VERMELHOS:     {mediaResto/1000}')
        print(f'O TEMPO DE LEITURA DOS ÚLTIMOS SINAIS RAM DE: {erroTotal/1000}')
        
        requisicao(urlNode1 + f'SINC?{mediaVermelhos}|{mediaResto}|{erroTotal + 200}|', timeout=0.2)
        requisicao(urlNode2 + f'SINC?{mediaVermelhos}|{mediaResto}|{erroTotal + 400}|', timeout=0.2)
        return True
    
    # A CADA VARIAÇÃO DE SINAL, INCREMENTE A VARIÁVEL E RESETE A CONTAGEM
    adicionarSinal(sinal)
    return False


# FUNÇÃO QUE ALTERA O SINAL LED DO RASPBERRY PARA MOSTRAR QUE TUDO ESTÁ FUNCIONANDO
def mudaLED():
    global estadoLED
    
    estadoLED = not estadoLED
    output(LED, estadoLED)


# FUNÇÃO PRINCIPAL DO PROGRAMA NO MODO LOOP ATÉ O SINCRONISMO
def main():
    global vermelhos, urlCamera, erroLeitura
    
    sleep(5)
    requisicao(urlNode1 + "RASPBERRY", timeout=5)

    while True:
        erroLeitura = time()

        try:
            WEBinfo = requisicao(urlCamera, timeout=0.5)
            img = np.array(bytearray(WEBinfo.content), dtype=np.uint8)
            img = cv2.imdecode(img, -1)

            img = zoom(img, 2)
            vermelhos = reconhecerVermelhos(img)
        except:
            print('erro na leitura da câmera...')
            continue

        sinal = processaSinal(vermelhos)      
        erroLeitura = time() - erroLeitura

        if verificarSincronismo(sinal):
            cleanup()
            exit()
            break


# ENVIAR UMA REQUISIÇÃO PARA UM LINK COM UM TEMPO MÁXIMO DE RESPOSTA
def requisicao(url, timeout):
    try:
        return requests.get(url, timeout=timeout)
    except Exception:
        return False


# RETORNANDO A MÉDIA DE UMA LISTA SEM OUTLIERS
def treatData(list):
    array = np.array(list)
    
    std  = np.std(array)
    mean = np.mean(array)

    upper = mean + 1*std
    lower = mean - 1*std

    array = array[(array > lower) & (array < upper)]
    return np.mean(array)


main()