import cv2, os
import numpy as np


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
        [[170, 127, 251], [180, 137, 261]],
        [[173, 135, 247], [183, 145, 257]],
        [[170, 168, 255], [180, 178, 265]],
        [[167, 102, 251], [177, 112, 261]],
        [[168, 151, 250], [178, 161, 260]],
        [[14, 129, 241], [24, 139, 251]],
        [[14, 106, 239], [24, 116, 249]],
        [[170, 123, 248], [180, 133, 258]],
        [[164, 139, 255], [174, 149, 265]],
        [[171, 163, 252], [181, 173, 262]],
        [[174, 141, 252], [184, 151, 262]],
        [[165, 168, 85], [175, 178, 95]],
        [[169, 176, 247], [179, 186, 257]],
        [[169, 168, 251], [179, 178, 261]]
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

    #cv2.imshow('a', maskr)
    #cv2.waitKey(0)

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
    vermelhos = reconhecerVermelhos(img)

    if len(vermelhos):
        img = desenharCirculos(img, vermelhos)

    cv2.imshow('Frame', img)
    cv2.waitKey(0)


#video('Teste/VideoSemaforo.mp4')
foto('Teste/Teste5.png')