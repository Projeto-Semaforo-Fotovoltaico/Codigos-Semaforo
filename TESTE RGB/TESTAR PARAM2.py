import cv2, os
import numpy as np
from time import time

pasta       = 'Teste'
param2teste = 15

# DADOS QUE SÃO OS INTERVALOS DE DETECÇÃO RGB
dadosRGB = np.array([
    [171, 184, 180], [181, 194, 190],
    [171, 158, 245], [181, 168, 255],
    [172, 157, 137], [182, 167, 147],
    [172, 186, 187], [182, 196, 197],
    [170, 158, 245], [180, 168, 255],
    [173, 201, 235], [183, 211, 245],
    [175, 172, 245], [185, 182, 255],
    [171, 199, 245], [181, 209, 255],
    [174, 107, 245], [184, 117, 255],
    [166, 65, 245], [176, 75, 255]
], dtype=np.uint8)


# CRIANDO UMA IMAGEM QUE APRESENTA APENAS O INTERVALO RGB ESCOLHIDO
def juntarIntervalos(HSV):
    global dadosRGB
    
    maskr = 0
    for c in range(0, len(dadosRGB), 2):
        low, high  = dadosRGB[c], dadosRGB[c + 1]
        maskr = cv2.bitwise_or(maskr, cv2.inRange(HSV, low, high))
    
    return maskr


# DESENHANDO OS CÍRCULOS EM UMA LISTA DE COORDENADAS
def desenharCirculos(img, detected):
    x, y, r = int(detected[0]), int(detected[1]), int(detected[2])
    img = cv2.circle(img, (x, y), r, (0, 255, 0), 5)

    return img


# RECONHECENDO O CÍRCULO MAIS VERMELHOS PRESENTE EM UMA IMAGEM
def reconhecerVermelhos(img):
    global param2teste

    HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    maskr = juntarIntervalos(HSV)

    redCircles = cv2.HoughCircles(maskr, cv2.HOUGH_GRADIENT, 1, minDist=10000,
                                     param1=50, param2=param2teste, minRadius=2, maxRadius=300)

    if redCircles is not None:
        return redCircles[0][0], maskr
    
    return None, maskr


# CONVERTENDO AS DUAS IMAGENS PARA MESMA DIMENSÃO E TAMANHO e MOSTRANDO LADO A LADO
def showImages(img1, img2):
    img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR) 

    result = cv2.hconcat([img1, img2])
    cv2.imshow("IMAGEM", result)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


# EXIBE E IDENTIFICA SINAIS VERMELHOS EM UMA FOTO
def foto(pasta, arquivo):
    endereco = pasta + rf'\{arquivo}'
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
    global param2teste

    arquivos = arquivosDiretorio(pasta)
    for i, arquivo in enumerate(arquivos):
        
        while True:
            print()

            print('ARQUIVO: ', arquivo)
            print('DIGITE -1 PARA PARA A PRÓXIMA IMAGEM')
            param2teste = int(input('DIGITE O PARAM2: '))
            
            if param2teste == -1:
                break
            
            foto(pasta, arquivo)

main()