import cv2, urllib.request
import numpy as np
from time import sleep, time
from RPi.GPIO import *

# VARIÁVEIS GLOBAIS PARA SEREM UTILIZADAS NAS FUNÇÕES DO ALGORÍTIMO
temposVermelho = np.array([])  # VETOR PARA ARMAZENAR OS TEMPOS DE DECÇÕES VERMELHO
temposResto    = np.array([])  # VETOR PARA ARMAZENAR OS TEMPOS DE DECÇÕES NÃO VERMELHO
atualizacao    = time()        # VARIÁVEL ARMAZENAR O TEMPO DA ÚLTIMA ATUALIZAÇÃO
estadoAnterior = False         # VARIÁVEL PARA ARMAZENAR O ESTADO ANTERIOR
erroLeitura    = 0             # VARIÁVEL PARA ARMAZENAR O ERRO (TEMPO PARA LEITURA)

# CONFIGURANDO OS PINOS DIGITAIS DO LED DO RASPBERRY
LED = 12
estadoLED = True

cleanup()
setmode(BOARD)
setup(LED, OUT)
output(LED, HIGH)

# VARIÁVEIS GLOBAIS PARA LINKS DE REQUISIÇÃO WEB SERVIDOR LOCAL
urlCamera   = 'http://192.168.4.6/'
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
    [0, 60, 245]    , [10, 70, 255],
    [175, 150, 150] , [185, 160, 160],
    [170, 150, 150] , [180, 160, 160],
    [170, 155, 150] , [180, 165, 160],
    [170, 150, 245] , [180, 160, 255],
    [170, 160, 245] , [180, 170, 255]
], dtype=np.uint8)

# OBTENDO E ARMAZENANDO O ATUAL QUADRO DA FILMAGEM 
def getImage(url):
    try:
        img = urllib.request.urlopen(url, timeout=5)
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
def zoom(img, zoom_factor=2):
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
                                         param1=50, param2=8, minRadius=5, maxRadius=300)

    if redCircles is not None:
        return True

    return False


# RETORNANDO O ESTADO DE DETECÇÃO ENCONTRADO PARA PREENCHER O VETOR
def processaSinal(vermelhos):
    if vermelhos:
        print('SEMÁFORO VERMELHO DETECTADO!')
        return True
    
    print('SEMÁFORO VERMELHO NÃO DETECTADO!')
    return False


# SE O SINAL MUDOU PARA VERMELHO, ARMAZENE O TEMPO DE SINAL NÃO VERMELHO (VICE-VERSA)
def adicionarSinal(sinal):
    global temposVermelho, temposResto, sinc, atualizacao, estadoAnterior
    tempoSinal = time() - atualizacao + 0.4
    
    if tempoSinal < 5:
        return

    if sinal:
        requisicao(urlNode1 + 'ATIVAR', timeout=0.2) # SINAL VERMELHO
        requisicao(urlNode2 + 'ATIVAR', timeout=0.2) # SINAL VERMELHO

        print(f'{tempoSinal} ADICIONADO AO SINAL NÃO VERMELHO')
        temposResto = np.append(temposResto, tempoSinal)
    else:
        requisicao(urlNode1 + 'DESATIVAR', timeout=0.2) # SINAL NÃO VERMELHO
        requisicao(urlNode2 + 'DESATIVAR', timeout=0.2) # SINAL NÃO VERMELHO

        print(f'{tempoSinal} ADICIONADO AO SINAL VERMELHO')
        temposVermelho = np.append(temposVermelho, tempoSinal) 

    estadoAnterior = sinal
    atualizacao    = time()


# VALIDANDO A PRECISÃO E EXATIDÃO DOS DADOS REGISTRADOS
def verificarSincronismo():
    global atualizacao, sinc, temposVermelho
    global estadoAnterior, urlNode1, urlNode2, erroLeitura

    if len(temposVermelho) < 15 or len(temposResto) < 15:
        return False
    
    if incertezaRelativa(temposVermelho[2:]) < 0.1 and incertezaRelativa(temposResto[2:]) < 0.1:
        return True
    
    return False


# ATIVANDO O MODO SÍNCRONO, ENVIANDO TODOS OS DADOS COLETADOS
def ativarSincronismo():
    global erroTotal, erroLeitura, temposVermelho, temposResto, urlNode1, urlNode2

    erroTotal      = int(erroLeitura * 1000) 
    mediaVermelhos = int(np.mean(treatData(temposVermelho[2:]))  * 1000)
    mediaResto     = int(np.mean(treatData(temposResto[2:]))     * 1000)

    print(f'MÉDIA DOS TEMPOS DE SINAIS VERMELHOS:         {mediaVermelhos/1000}')
    print(f'MÉDIA DOS TEMPOS DE SINAIS NÃO VERMELHOS:     {mediaResto/1000}')
    print(f'O TEMPO DE LEITURA DOS ÚLTIMOS SINAIS RAM DE: {erroTotal/1000}')
    
    requisicao(urlNode1 + f'SINC?{mediaVermelhos}A{mediaResto}A{erroTotal + 200}A', timeout=0.2)
    requisicao(urlNode2 + f'SINC?{mediaVermelhos}A{mediaResto}A{erroTotal + 400}A', timeout=0.2)


# FUNÇÃO QUE ALTERA O SINAL LED DO RASPBERRY PARA MOSTRAR QUE TUDO ESTÁ FUNCIONANDO
def mudaLED():
    global estadoLED
    
    estadoLED = not estadoLED
    output(LED, estadoLED)


# FUNÇÃO PRINCIPAL DO PROGRAMA NO MODO LOOP ATÉ O SINCRONISMO
def main():
    global urlCamera, erroLeitura, estadoAnterior
    requisicao(urlNode1 + "RASPBERRY", timeout=5)

    while True:
        erroLeitura = time()
        img = getImage(urlCamera + 'CAPTURE')
        
        if img is None:
            sleep(0.5)
            continue

        sinal = reconhecerVermelhos(zoom(img))
        erroLeitura = time() - erroLeitura
        mudaLED()    

        if sinal != estadoAnterior:
            adicionarSinal(sinal)
        
        if verificarSincronismo() and sinal:
            ativarSincronismo()
            cleanup()
            exit()


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


main()