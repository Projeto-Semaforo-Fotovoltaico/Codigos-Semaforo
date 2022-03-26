import cv2
import numpy as np

endrecoImagem = r'Semaforo2.png'

img = cv2.imread(endrecoImagem)
img = cv2.resize(img, (800, 600), interpolation=cv2.INTER_CUBIC)

minDist   = 50
param1    = 50
param2    = 20
minRadius = 10
maxRadius = 50

minX, maxX = 0,  10
minY, maxY = 50, 200


def listaCirculos(img):
    gray_blurred = cv2.blur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (3, 3))
    detected = cv2.HoughCircles(gray_blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=minDist,
                                param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)

    if detected is not None:  # SE ALGUM CÍRCULO FOI ENCONTRADO
        detected = np.around(detected)  # CONVERTENDO OS VALORES PARA INTEIRO
        return detected[0, :]


def desenharCirculo(img, x, y, r):
    # Draw the circumference of the circle.
    cv2.circle(img, (x, y), r, (0, 255, 0), 2)

    # Draw a small circle (of radius 1) to show the center.
    cv2.circle(img, (x, y), 1, (0, 0, 255), 3)


def reconhecerCirculos(img, detected):
    for circulo in detected:
        x, y, r = circulo[0], circulo[1], circulo[2]
        desenharCirculo(img, x, y, r)


def reconhecerSemáforos(lista):
    for i in range(0, len(lista)):
        x1, y1, r1 = lista[i][0], lista[i][1], lista[i][2]
        circulo1 = np.array([x1, y1, r1])

        listaCirculos = []
        x = 0
        for j in range(0, len(lista)):
            if i == j:
                continue

            x2, y2, r2 = lista[j][0], lista[j][1], lista[j][2]
            circulo2 = np.array([x2, y2, r2])

            diferencaX = abs(circulo2[0] - circulo1[0])
            diferencaY = abs(circulo2[1] - circulo1[1])

            if minX <= diferencaX <= maxX and minY <= diferencaY <= maxY:
                listaCirculos.append(circulo2)
                x += 1

            if x == 2:
                listaCirculos.append(circulo1)
                print('semáforo detectado!')
                return listaCirculos


lista = listaCirculos(img)
lista = reconhecerSemáforos(lista)

for x, y, r in lista:
    desenharCirculo(img, int(x), int(y), int(r))

x = [int(x) for x, y, r in lista]
y = [int(y) for x, y, r in lista]
r = [int(r) for x, y, r in lista]

img = cv2.rectangle(img, (min(x) - 2*max(r), min(y) - 2*max(r)), (max(x) + 2*max(r), max(y) + 2*max(r)),
                   (0, 0, 255), thickness=4)

cv2.imshow('Semaforo', img)
cv2.waitKey(0)