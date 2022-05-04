import cv2
import urllib.request
import numpy as np
import os
import requests

def hideTerminal():
    import win32gui, win32con
    the_program_to_hide = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(the_program_to_hide , win32con.SW_HIDE)


def conectarRede(networkName):
    os.system(f'''cmd /c "netsh wlan connect name={networkName}"''')


def run(url):
    # CRIANDO UMA JANELA PADRÃO MESMO SEM RECEBER A IMAGEM
    cv2.namedWindow("WEB IMAGE", cv2.WINDOW_AUTOSIZE)

    while True:
        # RECEBENDO AS INFORMAÇÕES CONTIDAS NO ENDEREÇO INDICADO
        try:
            WEBinfo = urllib.request.urlopen(url)
        except:
            continue

        # CONVERTENDO A INFORMAÇÃO PARA UM ARRAY DE BYTES TIPO UINT8
        img = np.array(bytearray(WEBinfo.read()), dtype=np.uint8)
        img = cv2.imdecode(img, -1)

        # MOSTRANDO A IMAGEM
        cv2.imshow('WEB IMAGE', img)
        key = cv2.waitKey(5)

        # SAINDO SE A TECLA 'q' FOR PRESSIONADA
        if key == ord('q'):
            break

    cv2.destroyAllWindows()

hideTerminal()
conectarRede('ProjetoSemaforo')
run('http://192.168.4.2/cam-hi.jpg')