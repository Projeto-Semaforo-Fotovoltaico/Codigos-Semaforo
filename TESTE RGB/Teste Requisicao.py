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
MAX = 20


# VARIÁVEIS GLOBAIS PARA LINKS DE REQUISIÇÃO WEB SERVIDOR LOCAL
networkName = 'ProjetoSemaforo'
urlCamera   = 'http://192.168.4.4/'
urlNode1    = 'http://192.168.4.1/'
urlNode2    = 'http://192.168.4.3/'


temposVermelho = [1660756706.8029473, 7.4204323291778564, 9.79878568649292, 9.149834632873535, 9.23647403717041, 7.526655197143555, 9.987699747085571, 11.137147426605225, 10.806663274765015, 11.548025131225586, 9.490761041641235, 9.409591674804688, 7.502420425415039, 16.51188635826111, 9.797597169876099, 9.86324691772461, 10.632050514221191, 10.787625789642334, 10.712761878967285, 10.536731004714966, 7.580240964889526, 11.360202550888062, 9.540639877319336, 8.985106945037842, 9.003581762313843, 14.566730737686157, 5.5254926681518555, 5.984116792678833, 13.347306966781616, 8.052519798278809, 10.199697732925415, 5.946701765060425, 9.07896113395691, 7.76341986656189, 9.426501035690308, 11.609013319015503, 13.639278173446655, 9.566927909851074, 9.815685987472534, 9.97891092300415, 12.534651041030884, 10.087493181228638, 9.778103113174438, 10.078441619873047, 9.42996335029602, 9.457921981811523, 10.09279465675354, 7.574396133422852, 11.56593370437622, 10.406388282775879]
temposResto = [7.876493453979492, 14.92185378074646, 16.0119309425354, 15.909299612045288, 17.10764169692993, 15.992376804351807, 13.985103845596313, 13.712345838546753, 14.149477243423462, 14.39583134651184, 21.162022352218628, 13.970776557922363, 15.526950120925903, 10.55150580406189, 10.232321739196777, 15.025108098983765, 14.579996109008789, 15.631982803344727, 12.54466462135315, 18.91655659675598, 13.523715496063232, 14.297078371047974, 15.795922994613647, 15.443443059921265, 16.023408889770508, 14.058064937591553, 22.975248098373413, 13.70899224281311, 16.016802072525024, 9.546492099761963, 19.788538932800293, 15.346869707107544, 16.72610902786255, 16.52517318725586, 14.873337268829346, 13.828620195388794, 15.504781007766724, 61.52138566970825, 13.705093145370483, 15.099740743637085, 12.201700687408447, 15.117384433746338, 15.447023630142212, 15.040236949920654, 15.74062180519104, 16.296757221221924, 16.039090394973755, 15.741312026977539, 13.188148736953735, 13.758830547332764]


# ENVIAR UMA REQUISIÇÃO PARA UM LINK COM UM TEMPO MÁXIMO DE RESPOSTA
def requisicao(url, timeout):
    try:
        return urllib.request.urlopen(url, timeout=timeout)
    except Exception:
        return False


# CONECTANDO A UMA REDE WIFI PELO PC ATRAVÉS DE SEU NOME PÚBLICO
def conectarRede(networkName):
    os.system(f'''cmd /c "netsh wlan connect name={networkName}"''')


# RETORNANDO A MÉDIA DE UMA LISTA SEM OUTLIERS
def treatData(list):
    array = np.array(list)
    
    std  = np.std(array)
    mean = np.mean(array)

    upper = mean + 2*std
    lower = mean - 2*std

    array = array[(array > lower) & (array < upper)]
    return np.mean(array)




conectarRede('ProjetoSemaforo')
sleep(1)

while True:
    print(requisicao(urlNode2 + 'ATIVAR3423423423???43423432423423', timeout=0.2))
    sleep(1)
    print(requisicao(urlNode2 + 'DESATIVAR34234234???23432423423', timeout=0.2))
    sleep(1)