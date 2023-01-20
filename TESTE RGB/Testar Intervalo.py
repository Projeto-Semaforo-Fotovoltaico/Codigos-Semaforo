import cv2, os
import numpy as np
from time import time

pasta = 'Teste'

# DADOS QUE SÃO OS INTERVALOS DE DETECÇÃO RGB
dadosRGB = np.array([
    [[6, 200, 244], [16, 210, 254]],
    [[22, 83, 219], [32, 93, 229]],
    [[0, 184, 250], [10, 194, 260]],
    [[4, 181, 252], [14, 191, 262]],
    [[6, 189, 251], [16, 199, 261]]
])


# CRIANDO UMA IMAGEM QUE APRESENTA APENAS O INTERVALO RGB ESCOLHIDO
def juntarIntervalos(HSV):
    global dadosRGB
    
    maskr = 0
    for c in range(len(dadosRGB)):
        low, high  = dadosRGB[c]
        maskr = cv2.add(maskr, cv2.inRange(HSV, low, high))
    
    return maskr


# DESENHANDO OS CÍRCULOS EM UMA LISTA DE COORDENADAS
def desenharCirculos(img, detected):
    x, y, r = int(detected[0]), int(detected[1]), int(detected[2])
    img = cv2.circle(img, (x, y), r, (0, 255, 0), 5)

    return img


# RECONHECENDO O CÍRCULO MAIS VERMELHOS PRESENTE EM UMA IMAGEM
def reconhecerVermelhos(img):
    HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    maskr = juntarIntervalos(HSV)

    redCircles = cv2.HoughCircles(maskr, cv2.HOUGH_GRADIENT, 1, minDist=80,
                                     param1=50, param2=15, minRadius=2, maxRadius=300)

    if redCircles is not None:
        return redCircles[0][0], maskr
    
    return None, maskr


# CONVERTENDO AS DUAS IMAGENS PARA MESMA DIMENSÃO E TAMANHO e MOSTRANDO LADO A LADO
def showImages(img1, img2):
    img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR) 
    img1 = cv2.resize(img1, (640, 480))
    img2 = cv2.resize(img2, (640, 480))

    result = cv2.hconcat([img1, img2])
    cv2.imshow("IMAGEM", result)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


# EXIBE E IDENTIFICA SINAIS VERMELHOS EM UMA FOTO
def foto(endereco):
    img = cv2.imread(endereco)
    
    tempo = time()
    redCircle, maskr = reconhecerVermelhos(img)
    print(f'TEMPO PARA RECONHECIMENTO: {time()-tempo:.3f} SEGUNDOS')

    if redCircle is not None:
        img = desenharCirculos(img, redCircle)

    showImages(img, maskr)


# RETORNA O NOME DE TODOS OS ARQUIVOS ENCONTRADOS EM UMA PASTA
def arquivosDiretorio(endereco=''):
        arquivos = []
        for caminho_diretorio, nome_diretorio, nome_arquivo in os.walk(endereco):
            if caminho_diretorio == endereco: 
                arquivos.extend(nome_arquivo)
                return arquivos


def main():
    arquivos = arquivosDiretorio(pasta)
    for i, arquivo in enumerate(arquivos):
        print(f'\nIMAGEM: {arquivo}')
        foto(pasta + rf'\{arquivo}')


main()