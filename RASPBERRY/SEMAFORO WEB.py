import urllib.request, os, cv2
import numpy as np
from time import sleep, time


# VARIÁVEIS GLOBAIS PARA SEREM UTILIZADAS NAS FUNÇÕES DO ALGORÍTIMO
temposVermelho = []     # VETOR PARA ARMAZENAR OS TEMPOS DE DECÇÕES VERMELHO
temposResto    = []     # VETOR PARA ARMAZENAR OS TEMPOS DE DECÇÕES NÃO VERMELHO
temposErro     = []     # VETOR PARA ARMAZENAR OS TEMPOS DE ERRO DE DETECÇÃO
sinc = 0                # VARIÁVEL PARA CONTAGEM DE DETECÇÕES
atualizacao = time()    # VARIÁVEL ARMAZENAR O TEMPO DA ÚLTIMA ATUALIZAÇÃO
vermelhos = False       # VARIÁVEL DE DETECÇÃO DO SINAL
estadoAnterior = False  # VARIÁVEL PARA ARMAZENAR O ESTADO ANTERIOR


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

    if sinal:
        print(f'{atualizacao} ADICIONADO AO SINAL NÃO VERMELHO')
        temposResto.append(atualizacao)
    else:
        print(f'{atualizacao} ADICIONADO AO SINAL VERMELHO')
        temposVermelho.append(atualizacao)
    
    sinc = sinc + 1          # INCREMENTANDO A SINCRONIZAÇÃO
    estadoAnterior = sinal   # ATUALIZANDO O ESTADO ANTERIOR
    atualizacao = time()     # ATUALIZANDO O TEMPO DE ATUALIZAÇÃO


# ADICIONANDO OS TEMPOS EM QUE O SINAL VERMELHO FICOU DESATIVADO
def verificarSincronismo(sinal):
    global atualizacao, sinc, temposVermelho, temposResto, temposErro
    global estadoAnterior, urlNode1, urlNode2

    # PRIMERIA VEZ QUE ENTRA NA FUNÇÃO, ESTABELEÇA AS CONDIÇÕES INICIAIS
    if sinc == 0:
        adicionarSinal(sinal)
        return False

    # SÓ PROSSEGUE SE O SINAL MUDAR DE ESTADO E DEMORAR MAIS QUE 5 SEGUNDOS (GARANTIA)
    if estadoAnterior == sinal or time() - atualizacao < 5:
        return False

    # ENCONTRANDO E ATUALIZANDO O TEMPO DE VARIAÇÃO DE SINAL
    atualizacao = time() - atualizacao
    
    # TOTAL DE VARIAÇÕES DE SINAL NECESSÁRIAS PARA SINCRONIZAÇÃO
    if sinc == 30:
        mediaVermelhos = np.mean(temposVermelho[2:])
        mediaResto     = np.mean(temposResto[2:])
        mediaErros     = np.mean(temposErro)

        print(f'MÉDIA DOS TEMPOS DE SINAIS VERMELHOS: {mediaVermelhos:.2f}')
        print(f'MÉDIA DOS TEMPOS DE SINAIS VERMELHOS: {mediaResto:.2f}')
        print(f'MÉDIA DOS ERROS DE TEMPO CALCULADOS:  {mediaErros:.2f}')

        requisicao(urlNode1, f'SINCMODE?{mediaVermelhos}|{mediaResto}|{mediaErros}|{int(sinal)}|', timeout=0.5)
        requisicao(urlNode2, f'SINCMODE?{mediaVermelhos}|{mediaResto}|{mediaErros}|{int(sinal)}|', timeout=0.5)
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
        tempo = time()
        WEBinfo = requisicao(urlCamera + 'cam-hi.jpg', timeout=2)

        if not WEBinfo:
            print('Sem Resposta')
            continue

        try:
            # CONVERTENDO A INFORMAÇÃO PARA UM ARRAY DE BYTES TIPO UINT8
            img = np.array(bytearray(WEBinfo.read()), dtype=np.uint8)
            img = cv2.imdecode(img, -1)
            vermelhos = reconhecerVermelhos(img)

            # REGISTRANDO O TEMPO QUE LEVA PARA A CÂMERA ENVIAR A IMAGEM
            temposErro.append(time() - tempo)

        except Exception:
            print('Erro ao passar imagem para Array!')
            continue

        sinal = processaSinal(vermelhos)      
        if verificarSincronismo(sinal):
            break

main()