from tkinter import E
import cv2, os
import numpy as np
from random import randint

ponto1 = (60, 20)
ponto2 = (100, 70)


# MOSTRANDO A IMAGEM PELO SEU OBJETO E ESPERANDO
def show(img):
    cv2.rectangle(img, ponto1, ponto2, (0, 255, 255), thickness=3)
    ret = cv2.resize(img, (800, 600), interpolation=cv2.INTER_CUBIC)

    cv2.imshow('imagem', ret)
    cv2.waitKey(0)


# DESENHANDO OS CÍRCULOS EM UMA LISTA DE COORDENADAS
def desenharCirculo(img, detected):
    if not len(detected):
        return

    x, y, r = int(detected[0]), int(detected[1]), int(detected[2])

    img = cv2.circle(img, (x, y), r, (0, 255, 0), 5)

    img = cv2.rectangle(img, (x - 1 * r, y - 1 * r),
                             (x + 1 * r, y + 1 * r),
                             (0, 0, 255), thickness=6)
    return img


# RECONHECENDO O CÍRCULO MAIS VERMELHO PRESENTE EM UMA IMAGEM
def reconhecerVermelho(img):
    HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    x1, y1, z1 = randint(0, 255), randint(0, 255), randint(0, 255)
    low = np.array([x1, y1, z1])

    high = np.array([x1+10, y1+10, z1+10])
    maskr = cv2.inRange(HSV, low, high)

    redCircles = cv2.HoughCircles(maskr, cv2.HOUGH_GRADIENT, 1, minDist=80,
                                     param1=50, param2=10, minRadius=5, maxRadius=500)

    if type(redCircles).__module__ == np.__name__:
        for circulo in redCircles:
            return validarPosicao(img, circulo[0], maskr, low, high)

    return []


# VERIFICANDO SE O SINAL ESTÁ ACIMA DA MENOR ALTURA ACEITA
def validarPosicao(img, redCircle, maskr, low, high):
    if (ponto1[0] <= redCircle[0] <= ponto2[0]) and (ponto1[1] <= redCircle[1] <= ponto2[1]):
        print()
        print('DETECTADO: ', f'[{low[0]}, {low[1]}, {low[2]}],', f'[{high[0]}, {high[1]}, {high[2]}]')
        show(maskr)
        return redCircle

    return []


# EXIBE TODAS AS FOTOS ENCONTRADAS EM UM ENDEREÇO
def fotos(endereco):
    show(cv2.imread(endereco))
    print('CARREGANDO', end='')

    while True:
        img = cv2.imread(endereco)
        vermelho = reconhecerVermelho(img)

        if len(vermelho):
            img = desenharCirculo(img, vermelho)
            show(img)

            print()
            print('CARREGANDO', end='')
        
        print('.', end='')


fotos('Teste\Teste2.png')