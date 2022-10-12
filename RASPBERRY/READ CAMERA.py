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


def requisicao(url, timeout):
    try:
        return urllib.request.urlopen(url, timeout=timeout)
    except Exception:
        return False


urlCamera = 'http://192.168.68.103'


def main():
    global urlCamera

    if not requisicao(urlCamera + ":81/stream", timeout=5):
        print('Câmera não está funcionando... Resetando ESP32')
        requisicao(urlCamera + r'\RESET', timeout=2)
        return main()

    cap = cv2.VideoCapture(urlCamera + ":81/stream")
    while True:
        erro = time()
        if not cap.isOpened():
            print('Erro na leitura da câmera...')
            sleep(0.5)
            continue
        
        try:
            ret, img = cap.read()
            erro = time() - erro

            print(f'erro: {erro:.5f}')
            cv2.imshow("streaming", img)
            cv2.waitKey(1)
        except:
            print('erro na leitura da câmera...')
            return main()
        
        

#hideTerminal()
#conectarRede('ProjetoSemaforo')
main()