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
erroLeitura = 0         # VARIÁVEL PARA ARMAZENAR O ERRO (TEMPO PARA LEITURA)
MAX = 20                # VARIÁVEL PARA TAMANHO MÁXIMO DO VETOR

# VARIÁVEIS GLOBAIS PARA LINKS DE REQUISIÇÃO WEB SERVIDOR LOCAL
networkName = 'ProjetoSemaforo'
urlCamera   = 'http://192.168.4.4'
urlNode1    = 'http://192.168.4.1/'
urlNode2    = 'http://192.168.4.3/'

# VARIÁVEIS GLOBAIS PARA FUNÇÃO DE MÉDIA MÓVEL PARA FILTRO LÓGICO
vetorLogico = np.zeros(10)
erroTotal   = 0.05 * len(vetorLogico) + 0.1
soma = 0
k = 0

# DADOS QUE SÃO OS INTERVALOS DE DETECÇÃO RGB
intervalos = [
    [[2, 205, 243], [12, 215, 253]],
    [[2, 214, 243], [12, 224, 253]],
    [[4, 207, 246], [14, 217, 256]],
    [[4, 181, 254], [14, 191, 264]],
    [[0, 197, 247], [10, 207, 257]],
    [[4, 224, 220], [14, 234, 230]],
    [[1, 186, 251], [11, 196, 261]],
    [[4, 218, 231], [14, 228, 241]],
    [[2, 191, 251], [12, 201, 261]]
]
dadosMask = list(range(len(dadosRGB)))


# VERIFICANDO SE EXISTE ALGUM CÍRCULO VERMELHO NA IMAGEM
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
    global dadosRGB, dadosMask

    for c in range(len(dadosRGB)):
        low  = np.array(dadosRGB[c][0])
        high = np.array(dadosRGB[c][1])
        dadosMask[c] = cv2.inRange(HSV, low, high)

    mask = 0
    for c in range(len(dadosRGB)):
        mask = cv2.add(mask, dadosMask[c])
    return mask


# RETORNANDO O ESTADO DE DETECÇÃO ENCONTRADO PARA PREENCHER O VETOR
def processaSinal(vermelhos):
    if smooth(int(vermelhos)) > 0.5:
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
        mediaVermelhos = int((treatData(temposVermelho[2:]) + erroTotal) * 1000)
        mediaResto     = int((treatData(temposResto[2:])    + erroTotal) * 1000)
        erroLeitura    = int(erroLeitura*1000)

        print(f'MÉDIA DOS TEMPOS DE SINAIS VERMELHOS:      {mediaVermelhos/1000}')
        print(f'MÉDIA DOS TEMPOS DE SINAIS NÃO VERMELHOS:  {mediaResto/1000}')
        print(f'O TEMPO DE LEITURA DO ÚLTIMO SINAL FOI DE: {erroLeitura/1000}')
        
        requisicao(urlNode1 + f'SINC?{mediaVermelhos}|{mediaResto}|{erroLeitura + 200}|', timeout=0.2)
        requisicao(urlNode2 + f'SINC?{mediaVermelhos}|{mediaResto}|{erroLeitura + 400}|', timeout=0.2)
        return True
    
    # A CADA VARIAÇÃO DE SINAL, INCREMENTE A VARIÁVEL E RESETE A CONTAGEM
    adicionarSinal(sinal)
    return False


# FUNÇÃO PRINCIPAL DO PROGRAMA NO MODO LOOP ATÉ O SINCRONISMO
def main():
    global networkName, vermelhos, urlCamera, erroLeitura
    conectarRede(networkName)
    
    sleep(5)
    requisicao(urlNode1 + "RASPBERRY", timeout=5)

    if not requisicao(urlCamera + ":81/stream", timeout=10):
        print('Câmera não está funcionando... Resetando ESP32')
        requisicao(urlCamera + r'\RESET', timeout=2)
        sleep(5)
        return main()

    requisicao(urlCamera + "/control?var=quality&val=30", timeout=5)
    requisicao(urlCamera + "/control?var=framesize&val=9", timeout=5)

    sleep(1)
    cap = cv2.VideoCapture(urlCamera + ":81/stream")

    while True:
        erroLeitura = time()
        if not cap.isOpened():
            print('Erro na leitura da câmera...')
            sleep(0.5)
            continue
        
        try:
            ret, img = cap.read()
            vermelhos = reconhecerVermelhos(img)
            erroLeitura = time() - erroLeitura
        except:
            print('erro na leitura da câmera...')
            return main()

        sinal = processaSinal(vermelhos)      
        if verificarSincronismo(sinal):
            break


# ENVIAR UMA REQUISIÇÃO PARA UM LINK COM UM TEMPO MÁXIMO DE RESPOSTA
def requisicao(url, timeout):
    try:
        return urllib.request.urlopen(url, timeout=timeout)
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


# FILTRANDO UMA FUNÇÃO POR MÉDIA MÓVEL
def smooth(val):
    global soma, k, vetorLogico

    soma = soma - vetorLogico[k]
    vetorLogico[k] = val

    soma = soma + vetorLogico[k]
    k = k + 1

    if k == len(vetorLogico):
        k = 0
    
    return soma/vetorLogico.size
    

# CONECTANDO A UMA REDE WIFI PELO PC ATRAVÉS DE SEU NOME PÚBLICO
def conectarRede(networkName):
    os.system(f'''cmd /c "netsh wlan connect name={networkName}"''')


main()