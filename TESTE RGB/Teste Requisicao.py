import urllib.request, os, cv2
import numpy as np
from time import sleep, time

sleep(5)
listaTTGO = []
listaNODE = []


# ENVIAR UMA REQUISIÇÃO PARA UM LINK COM UM TEMPO MÁXIMO DE RESPOSTA
def requisicao(url, timeout):
    try:
        return urllib.request.urlopen(url, timeout=timeout)
    except Exception:
        return False


# CONECTANDO A UMA REDE WIFI PELO PC ATRAVÉS DE SEU NOME PÚBLICO
def conectarRede(networkName):
    os.system(f'''cmd /c "netsh wlan connect name={networkName}"''')


# CALCULAR O ERRO => TEMPO QUE LEVA PARA OS MICROCONTROLADORES RECEBEREM AS REQUISIÇÕES
conectarRede('ProjetoSemaforo')
for c in range(0, 100):
    tempoNODE = time()
    requisicao('http://192.168.4.1/QUALQUERCOISA')
    tempoTTGO = time() - tempoNODE
    requisicao('http://192.168.4.3/QUALQUERCOISA')
    tempoNODE = time() - tempoNODE

    listaTTGO.append(tempoTTGO)
    listaNODE.append(tempoNODE)

    print(f'TEMPO TTGO: {tempoTTGO}')
    print(f'TEMPO NODE: {tempoNODE}')
    print()

print(f'MÉDIA TTGO: {np.mean(listaTTGO):.3f}')
print(f'MÉDIA NODE: {np.mean(listaNODE):.3f}')

