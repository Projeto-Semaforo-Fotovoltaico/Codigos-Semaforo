import urllib.request
from time import sleep
import os


def conectarRede(networkName):
    os.system(f'''cmd /c "netsh wlan connect name={networkName}"''')


def requisicao(url):
    try:
        return urllib.request.urlopen(url)
    except Exception:
        return False


while True:
    for c in range(0, 15):
        req = requisicao('http://192.168.4.1/ATIVAR')

        if req:
            print('ATIVANDO')
        else:
            conectarRede('ProjetoSemaforo')

        sleep(0.5)

    sleep(15)