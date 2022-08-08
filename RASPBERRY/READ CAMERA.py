import cv2
import urllib.request
import numpy as np
import os
from time import sleep
from time import time


def hideTerminal():
    import win32gui, win32con
    the_program_to_hide = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(the_program_to_hide , win32con.SW_HIDE)


def conectarRede(networkName):
    os.system(f'''cmd /c "netsh wlan connect name={networkName}"''')


def run(url):
    lista = []

    # CRIANDO UMA JANELA PADRÃO MESMO SEM RECEBER A IMAGEM
    cv2.namedWindow("WEB IMAGE", cv2.WINDOW_AUTOSIZE)

    while True:
        # RECEBENDO AS INFORMAÇÕES CONTIDAS NO ENDEREÇO INDICADO
        try:
            tempo = time()

            WEBinfo = urllib.request.urlopen(url, timeout=5)
            img = np.array(bytearray(WEBinfo.read()), dtype=np.uint8)
            img = cv2.imdecode(img, -1)

            tempo = round(time() - tempo, 2)
            lista.append(tempo)

            print('TEMPO PARA LEITURA: ', tempo)

        except:
            print('sem leitura')
            sleep(0.1)
            continue

        # MOSTRANDO A IMAGEM
        cv2.imshow('WEB IMAGE', img)
        key = cv2.waitKey(1)

        # SAINDO SE A TECLA 'q' FOR PRESSIONADA
        if key == ord('q'):
            break

        if len(lista) == 10:
            print()
            print(lista)
            break

    cv2.destroyAllWindows()

#hideTerminal()
conectarRede('ProjetoSemaforo')
run('http://192.168.4.4/cam-hi.jpg')