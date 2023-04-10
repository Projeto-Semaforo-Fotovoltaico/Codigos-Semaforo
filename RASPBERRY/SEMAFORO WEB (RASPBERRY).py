import os, cv2, urllib.request
import numpy as np
from time import sleep, time
from RPi.GPIO import *

# VARIÁVEIS GLOBAIS PARA SEREM UTILIZADAS NAS FUNÇÕES DO ALGORÍTIMO
temposVermelho = np.array([])  # VETOR PARA ARMAZENAR OS TEMPOS DE DECÇÕES VERMELHO
temposResto    = np.array([])  # VETOR PARA ARMAZENAR OS TEMPOS DE DECÇÕES NÃO VERMELHO
atualizacao = time()           # VARIÁVEL ARMAZENAR O TEMPO DA ÚLTIMA ATUALIZAÇÃO
estadoAnterior = False         # VARIÁVEL PARA ARMAZENAR O ESTADO ANTERIOR
erroLeitura = 0                # VARIÁVEL PARA ARMAZENAR O ERRO (TEMPO PARA LEITURA)
sinc = 0                       # VARIÁVEL PARA CONTAGEM DE DETECÇÕES 

# CONFIGURANDO OS PINOS DIGITAIS DO LED DO RASPBERRY
LED = 12
estadoLED = True

cleanup()
setmode(BOARD)
setup(LED, OUT)
output(LED, HIGH)

# VARIÁVEIS GLOBAIS PARA LINKS DE REQUISIÇÃO WEB SERVIDOR LOCAL
urlCamera   = 'http://192.168.4.6/CAPTURE'
urlNode1    = 'http://192.168.4.1/'
urlNode2    = 'http://192.168.4.3/'

# TABELA T-STUDENT PAR PRECISÃO E EXATIDÃO DOS DADOS POR INCERTEZA RELATIVA
tStudent = [
    12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.265, 2.306, 2.262, 2.228, 2.201, 2.179,
    2.160, 2.145, 2.131, 2.120, 2.110, 2.101, 2.093, 2.086, 2.080, 2.074, 2.069, 2.064,
    2.060, 2.056, 2.052, 2.048, 2.045, 2.042
]


# DADOS QUE SÃO OS INTERVALOS DE DETECÇÃO RGB
dadosRGB = np.array([
    [171, 184, 180], [181, 194, 190],
    [171, 158, 245], [181, 168, 255],
    [172, 157, 137], [182, 167, 147],
    [172, 186, 187], [182, 196, 197],
    [170, 158, 245], [180, 168, 255],
    [173, 201, 235], [183, 211, 245],
    [175, 172, 245], [185, 182, 255],
    [171, 199, 245], [181, 209, 255],
    [174, 107, 245], [184, 117, 255],
    [166, 65, 245] , [176, 75, 255]
], dtype=np.uint8)



# OBTENDO E ARMAZENANDO O ATUAL QUADRO DA FILMAGEM 
def getImage(url):
    try:
        img = urllib.request.urlopen(url, timeout=4)
        img = np.array(bytearray(img.read()), dtype=np.uint8)
    except:
        return None
    
    return cv2.imdecode(img, -1)


# CRIANDO UMA IMAGEM QUE APRESENTA APENAS O INTERVALO RGB ESCOLHIDO
def juntarIntervalos(HSV):
    global dadosRGB
    
    maskr = 0
    for c in range(0, len(dadosRGB), 2):
        low, high  = dadosRGB[c], dadosRGB[c + 1]
        maskr = cv2.bitwise_or(maskr, cv2.inRange(HSV, low, high))
    
    return maskr


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

    if redCircles is not None:
        return True

    return False


# SE O SINAL MUDOU PARA VERMELHO, ARMAZENE O TEMPO DE SINAL NÃO VERMELHO (VICE-VERSA)
def adicionarSinal(sinal):
    global temposVermelho, temposResto, sinc, atualizacao, estadoAnterior

    if sinal:
        requisicao(urlNode2 + 'SINAL', timeout=0.2) # SINAL VERMELHO
        requisicao(urlNode1 + 'SINAL', timeout=0.2) # SINAL VERMELHO

        print(f'{atualizacao} ADICIONADO AO SINAL NÃO VERMELHO')
        temposResto = np.append(temposResto, atualizacao)
    else:
        requisicao(urlNode2 + 'SINAL', timeout=0.2) # SINAL NÃO VERMELHO
        requisicao(urlNode1 + 'SINAL', timeout=0.2) # SINAL NÃO VERMELHO

        print(f'{atualizacao} ADICIONADO AO SINAL VERMELHO')
        temposVermelho = np.append(temposVermelho, atualizacao)

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
    if validarDados(temposVermelho[1:], temposResto[1:]) and sinal:
        erroTotal      = int(erroLeitura * 1000) + 8000
        mediaVermelhos = int(np.mean(treatData(temposVermelho[1:]))  * 1000)
        mediaResto     = int(np.mean(treatData(temposResto[1:]))     * 1000)

        print(f'MÉDIA DOS TEMPOS DE SINAIS VERMELHOS:         {mediaVermelhos/1000}')
        print(f'MÉDIA DOS TEMPOS DE SINAIS NÃO VERMELHOS:     {mediaResto/1000}')
        print(f'O TEMPO DE LEITURA DOS ÚLTIMOS SINAIS RAM DE: {erroTotal/1000}')
        
        requisicao(urlNode1 + f'SINC?{mediaVermelhos}A{mediaResto}A{erroTotal + 200}A', timeout=0.2)
        requisicao(urlNode2 + f'SINC?{mediaVermelhos}A{mediaResto}A{erroTotal + 400}A', timeout=0.2)
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
    requisicao(urlNode1 + "RASPBERRY", timeout=5)

    while True:
        erroLeitura = time()
        img = getImage(urlCamera)
        
        if img is None:
            print('SEM IMAGEM')
            sleep(0.5)
            return main()

        sinal = reconhecerVermelhos(img)
        
        mudaLED()    
        erroLeitura = time() - erroLeitura
        if verificarSincronismo(sinal):
            cleanup()
            exit()
            break


# ENVIAR UMA REQUISIÇÃO PARA UM LINK COM UM TEMPO MÁXIMO DE RESPOSTA
def requisicao(url, timeout):
    try:
        return urllib.request.urlopen(url, timeout=timeout)
    except Exception:
        return False


# RETORNANDO A MÉDIA DE UMA LISTA SEM OUTLIERS
def treatData(array):
    if len(array) < 5:
        return array
    
    std  = np.std(array)
    mean = np.mean(array)

    upper = mean + 1*std
    lower = mean - 1*std

    return array[(array > lower) & (array < upper)]


# CALCULANDO A INCERTEZA RELATIVA EM UMA LISTA DE DADOS
def incertezaRelativa(array):
    global tStudent
    n = len(array)
    T = 1

    if n <= 30:
        T = tStudent[n-2]  

    return T * np.std(array, ddof = 1)/(n**0.5)/np.mean(array)


# VALIDANDO A PRECISÃO E EXATIDÃO DOS DADOS REGISTRADOS
def validarDados(array1, array2):
    if len(array1) < 5 or len(array2) < 5:
        return False
    
    if incertezaRelativa(array1) < 0.4 and incertezaRelativa(array2) < 0.4:
        return True
    
    return False


main()