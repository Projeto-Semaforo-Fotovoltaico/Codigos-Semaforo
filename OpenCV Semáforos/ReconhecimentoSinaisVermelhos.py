import cv2
import numpy as np


# MOSTRANDO A IMAGEM PELO SEU OBJETO E ESPERANDO
def show(img):
    img = cv2.resize(img, (800, 600), interpolation=cv2.INTER_CUBIC)
    cv2.imshow('imagem', img)
    cv2.waitKey(0)


# DESENHANDO OS CÍRCULOS EM UMA LISTA DE COORDENADAS
def desenharCirculos(img, detected):
    if not len(detected):
        return

    x, y, r = int(detected[0]), int(detected[1]), int(detected[2])

    img = cv2.circle(img, (x, y), r, (0, 255, 0), 2)

    img = cv2.rectangle(img, (x - 3 * r, y - 3 * r),
                             (x + 3 * r, y + 3 * r),
                             (0, 0, 255), thickness=4)
    return img


def validar(img, redCircles):
    profundidadeLimite = int(img.shape[0]/2) # METADE DA FIGURA

    largura = img.shape[1]
    cv2.line(img, (0, profundidadeLimite), (largura, profundidadeLimite), (0, 255, 255), thickness=3)

    if type(redCircles).__module__ == np.__name__:
        for coordenadas in redCircles[0]:
            if coordenadas[1] <= profundidadeLimite:
                return coordenadas
    return []


# RECONHECENDO O CÍRCULO MAIS VERMELHOS PRESENTE EM UMA IMAGEM
def reconhecerVermelhos(img):
    HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    minVerm = 254
    while minVerm != 120:
        lower_red1 = np.array([0, 70, minVerm])
        upper_red1 = np.array([10, 220, 255])  # green estava em 255

        lower_red2 = np.array([170, 70, minVerm])
        upper_red2 = np.array([180, 220, 255])  # green estava em 255

        # DESTACANDO OS TONS DE VERMELHO (USANDO DOIS INTERVALOS DESEJADOS)
        mask1 = cv2.inRange(HSV, lower_red1, upper_red1)
        mask2 = cv2.inRange(HSV, lower_red2, upper_red2)
        maskr = cv2.add(mask1, mask2)

        redCircles = cv2.HoughCircles(maskr, cv2.HOUGH_GRADIENT, 1, minDist=80,
                                         param1=50, param2=15, minRadius=5, maxRadius=60)

        lista = validar(img, redCircles)

        if len(lista):
            print(minVerm)
            show(maskr)
            return lista

        minVerm -= 1

    return []


# CÓDIGO PRINCIPAL
for c in range(1, 22):
    endereco = r'FotosSemaforo/Semaforo' + str(c) + '.png'
    img = cv2.imread(endereco)

    print(endereco)
    vermelhos = reconhecerVermelhos(img)

    if len(vermelhos):
        img = desenharCirculos(img, vermelhos)

    show(img)
    print()
