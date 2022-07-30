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


# RECONHECENDO O CÍRCULO MAIS VERMELHOS PRESENTE EM UMA IMAGEM
def reconhecerVermelhos(img):
    HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    low1 = np.array([14, 129, 241])
    high1 = np.array([24, 139, 251])

    low2 = np.array([14, 106, 239])
    high2 = np.array([24, 116, 249])

    mask1 = cv2.inRange(HSV, low1, high1)
    mask2 = cv2.inRange(HSV, low2, high2)

    maskr = cv2.add(mask1, mask2)
    redCircles = cv2.HoughCircles(maskr, cv2.HOUGH_GRADIENT, 1, minDist=80,
                                     param1=50, param2=9.9, minRadius=5, maxRadius=300)

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


video('Teste/VideoSemaforo.mp4')