import cv2
import urllib.request
import numpy as np

def run(url):
    # CRIANDO UMA JANELA PADRÃO MESMO SEM RECEBER A IMAGEM
    cv2.namedWindow("WEB IMAGE", cv2.WINDOW_AUTOSIZE)

    while True:
        # RECEBENDO AS INFORMAÇÕES CONTIDAS NO ENDEREÇO INDICADO
        WEBinfo = urllib.request.urlopen(url)

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

run('http://192.168.151.170/cam-hi.jpg')