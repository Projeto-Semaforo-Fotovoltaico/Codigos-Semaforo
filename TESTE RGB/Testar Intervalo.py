import cv2, os
import numpy as np
from time import time


# DESENHANDO OS CÍRCULOS EM UMA LISTA DE COORDENADAS
def desenharCirculos(img, detected):
    if not len(detected):
        return

    x, y, r = int(detected[0]), int(detected[1]), int(detected[2])
    img = cv2.circle(img, (x, y), r, (0, 255, 0), 5)

    img = cv2.rectangle(img, (x - 1 * r, y - 1 * r),
                             (x + 1 * r, y + 1 * r),
                             (0, 0, 255), thickness=6)
    return img


def juntarIntervalos(HSV):
    intervalos = [
        [[174, 132, 245], [184, 142, 255]],
        [[171, 145, 254], [181, 155, 264]],
        [[175, 169, 245], [185, 179, 255]],
        [[168, 172, 253], [178, 182, 263]],
        [[172, 189, 251], [182, 199, 261]],
        [[170, 158, 255], [180, 168, 265]],
        [[165, 139, 74], [175, 149, 84]],
        [[174, 171, 247], [184, 181, 257]],
        [[172, 207, 128], [182, 217, 138]],
        [[170, 210, 128], [180, 220, 138]],
        [[169, 212, 81], [179, 222, 91]],
        [[170, 214, 249], [180, 224, 259]],
        [[175, 233, 198], [185, 243, 208]],
        [[175, 236, 179], [185, 246, 189]]
    ]
    
    for c in range(len(intervalos)):
        low  = np.array(intervalos[c][0])
        high = np.array(intervalos[c][1])
        intervalos[c] = cv2.inRange(HSV, low, high)

    mask = intervalos[0]
    for c in range(1, len(intervalos)):
        mask = cv2.add(mask, intervalos[c])

    return mask


# RECONHECENDO O CÍRCULO MAIS VERMELHOS PRESENTE EM UMA IMAGEM
def reconhecerVermelhos(img):
    HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    maskr = juntarIntervalos(HSV)

    cv2.imshow('MASK', maskr)
    cv2.waitKey(0)

    redCircles = cv2.HoughCircles(maskr, cv2.HOUGH_GRADIENT, 1, minDist=80,
                                     param1=50, param2=10, minRadius=2, maxRadius=300)

    if type(redCircles).__module__ == np.__name__:
        for circulo in redCircles:
            return circulo[0]
    
    return []


# EXIBE E IDENTIFICA SINAIS VERMELHOS EM UM VÍDEO
def video(endereco):
    cap = cv2.VideoCapture(endereco)

    if cap.isOpened()== False:
      print("Error opening video  file")

    while cap.isOpened():
        ret, frame = cap.read()
        if ret == True:
            frame = cv2.resize(frame, (800, 600), interpolation=cv2.INTER_CUBIC)
            vermelhos = reconhecerVermelhos(frame)

            if len(vermelhos):
                img = desenharCirculos(frame, vermelhos)

            cv2.imshow('Frame', frame)

            if cv2.waitKey(25) & 0xFF == ord('q'):
              break
        else:
            break

    cap.release()
    cv2.destroyAllWindows()


# EXIBE E IDENTIFICA SINAIS VERMELHOS EM UMA FOTO
def foto(endereco):
    img = cv2.imread(endereco)

    tempo = time()
    vermelhos = reconhecerVermelhos(img)
    print(f'TEMPO PARA RECONHECIMENTO: {time()-tempo:.3f} SEGUNDOS!')

    if len(vermelhos):
        img = desenharCirculos(img, vermelhos)

    cv2.imshow('Frame', img)
    cv2.waitKey(0)


#video('Teste/VideoSemaforo.mp4')
foto('Teste/Teste5.png')